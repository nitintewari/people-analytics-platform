"""
Generates ats_export.csv (Greenhouse-style) and id_bridge.csv
Key: CandidateID (different from EmployeeID — that's the point)
"""
import numpy as np
import pandas as pd
import re
from faker import Faker

fake = Faker()
Faker.seed(42)
np.random.seed(42)

hris = pd.read_csv("data/hris_export.csv")
N = len(hris)

names = [fake.name() for _ in range(N)]

hire_sources = [
    "Employee Referral", "LinkedIn", "Indeed",
    "Career Site", "Recruiter Sourced", "University Recruiting"
]

ats_rows = []
for i, row in hris.iterrows():
    ats_rows.append({
        "CandidateID": 9000 + row["EmployeeID"],
        "CandidateName": names[i],
        "Department": row["Department"],
        "RoleHiredFor": row["JobRole"],
        "HireSource": np.random.choice(
            hire_sources, p=[.27, .22, .15, .15, .13, .08]),
        "TimeToHireDays": int(np.clip(
            np.random.normal(34, 13), 7, 95)),
        "HireDate": fake.date_between(
            start_date="-8y", end_date="today"),
    })

ats = pd.DataFrame(ats_rows)

# 8% name drift — forces fuzzy matching in validation
# Robert -> Bob, Jennifer -> Jen etc.
nickname_map = {
    "Robert": "Bob", "William": "Bill", "Richard": "Rick",
    "Elizabeth": "Liz", "Michael": "Mike", "Katherine": "Kate",
    "Jennifer": "Jen", "Christopher": "Chris"
}

drift_idx = np.random.choice(ats.index, int(0.08 * N), replace=False)
for idx in drift_idx:
    full = ats.at[idx, "CandidateName"]
    first = full.split()[0]
    if first in nickname_map:
        ats.at[idx, "CandidateName"] = full.replace(
            first, nickname_map[first])
    else:
        parts = full.split()
        if len(parts) == 2:
            ats.at[idx, "CandidateName"] = (
                f"{parts[0]} {parts[1][0]}. {parts[1]}")

ats.to_csv("data/ats_export.csv", index=False)
print(f"ATS records: {len(ats)}")
print(f"Name drift introduced: {len(drift_idx)} records")

# Bridge file — maps EmployeeID <-> CandidateID <-> Email
def make_email(name):
    parts = re.sub(r"[^a-zA-Z ]", "", name).lower().split()
    return (f"{parts[0]}.{parts[-1]}@company.com"
            if len(parts) > 1 else f"{parts[0]}@company.com")

bridge = pd.DataFrame({
    "EmployeeID": hris["EmployeeID"],
    "CandidateID": 9000 + hris["EmployeeID"],
    "TrueName": names,
    "Email": [make_email(n) for n in names],
})
bridge.to_csv("data/id_bridge.csv", index=False)
print(f"Bridge file: {len(bridge)} rows")