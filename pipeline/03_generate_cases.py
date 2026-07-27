"""
Generates case_log.csv — simulates ServiceNow HR case export
Key: Email (third key type — not EmployeeID, not CandidateID)
Ticket volume correlated with real signals from HRIS
"""
import numpy as np
import pandas as pd

hris = pd.read_csv("data/hris_export.csv")
bridge = pd.read_csv("data/id_bridge.csv")
merged = hris.merge(bridge, on="EmployeeID")

categories = [
    "Payroll", "Benefits", "Policy Question", "IT Access",
    "Manager Escalation", "PTO Request", "Comp Inquiry"
]

np.random.seed(42)
case_rows = []

for _, row in merged.iterrows():
    # Rate driven by real signals — not random
    # Disengaged employees file more tickets
    rate = 1.8
    rate += (row["JobSatisfaction"] <= 2) * 2.4
    rate += (row["EngagementScore"] <= 2) * 1.6
    rate += (row["WorkLifeBalance"] == 1) * 1.9
    rate += (row["OverTime"] == "Yes") * 0.9
    rate += (row["Department"] == "News & Content") * 1.1

    n_tickets = int(np.clip(np.random.poisson(rate), 0, 20))

    for _ in range(n_tickets):
        case_rows.append({
            "Email": row["Email"],
            "TicketCategory": np.random.choice(categories),
            "DaysToResolve": int(np.clip(
                np.random.exponential(3), 0, 30)),
            "Escalated": np.random.choice([0, 1], p=[.86, .14]),
        })

df = pd.DataFrame(case_rows)
df.to_csv("data/case_log.csv", index=False)

print(f"Total tickets: {len(df)}")
print(f"Employees with tickets: {df['Email'].nunique()}")
print(f"Avg per employee: {len(df)/len(merged):.1f}")
print(f"\nCategory breakdown:\n{df['TicketCategory'].value_counts()}")