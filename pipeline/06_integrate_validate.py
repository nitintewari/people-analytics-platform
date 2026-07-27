"""
Integrates 3 sources + validates identity matches
Output: output/analytics_ready.csv (single source of truth)
        output/data_quality_report.csv (flagged records)
"""
import pandas as pd
from difflib import SequenceMatcher

hris   = pd.read_csv("data/hris_export.csv")
ats    = pd.read_csv("data/ats_export.csv")
bridge = pd.read_csv("data/id_bridge.csv")
cases  = pd.read_csv("data/case_log.csv")

# JOIN 1: HRIS + bridge + ATS
df = (hris
      .merge(bridge, on="EmployeeID", how="left")
      .merge(
          ats[["CandidateID", "CandidateName", "HireSource",
               "TimeToHireDays", "HireDate"]],
          on="CandidateID", how="left"
      ))

def first_name_sim(a, b):
    if pd.isna(a) or pd.isna(b): return 0.0
    fa = str(a).lower().split()[0]
    fb = str(b).lower().split()[0]
    return SequenceMatcher(None, fa, fb).ratio()

df["NameMatchScore"] = df.apply(
    lambda r: first_name_sim(r["TrueName"], r["CandidateName"]), axis=1)
df["MatchStatus"] = df["NameMatchScore"].apply(
    lambda s: "OK" if s >= 0.6 else "REVIEW")

# Flag don't drop — audit trail for every run
flagged = df[df["MatchStatus"] == "REVIEW"][[
    "EmployeeID", "TrueName", "CandidateName", "NameMatchScore"
]]
flagged.to_csv("output/data_quality_report.csv", index=False)

print(f"Total: {len(df)}")
print(f"Passed: {(df.MatchStatus=='OK').sum()}")
print(f"Flagged: {len(flagged)}")
print(f"Pass rate: {(df.MatchStatus=='OK').mean():.1%}")

# JOIN 2: ticket aggregates via email
ticket_agg = (cases
    .groupby("Email")
    .agg(TicketCount=("TicketCategory","count"),
         EscalatedTickets=("Escalated","sum"),
         AvgResolveDays=("DaysToResolve","mean"))
    .reset_index())
df = df.merge(ticket_agg, on="Email", how="left")
df["TicketCount"]      = df["TicketCount"].fillna(0).astype(int)
df["EscalatedTickets"] = df["EscalatedTickets"].fillna(0).astype(int)
df["AvgResolveDays"]   = df["AvgResolveDays"].fillna(0.0)

# Governance: drop PII-adjacent columns
# Identity crosswalk never reaches analytics table
analytics = df.drop(columns=["TrueName", "CandidateName", "Email"])
analytics.to_csv("output/analytics_ready.csv", index=False)

print(f"\nAnalytics-ready: {analytics.shape[0]} rows, "
      f"{analytics.shape[1]} columns")