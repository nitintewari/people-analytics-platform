"""
Generates hris_export.csv — simulates UKG Pro HRIS export
Key: EmployeeID
"""
import numpy as np
import pandas as pd

np.random.seed(42)
N = 1470

departments = ["Sales", "News & Content", "Human Resources",
               "Engineering", "Finance"]
dept_weights = [0.28, 0.42, 0.06, 0.14, 0.10]

job_roles = {
    "Sales": ["Account Executive", "Sales Manager", "Sales Coordinator"],
    "News & Content": ["Producer", "Reporter", "Editor",
                       "News Director", "Photojournalist"],
    "Human Resources": ["HR Generalist", "HR Manager"],
    "Engineering": ["Broadcast Engineer", "Systems Engineer", "IT Support"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Manager"],
}

rows = []
for emp_id in range(1, N + 1):
    dept = np.random.choice(departments, p=dept_weights)
    role = np.random.choice(job_roles[dept])
    age = int(np.clip(np.random.normal(38, 10), 21, 64))
    tenure = round(float(np.clip(
             np.random.exponential(4.5), 0.1, age - 20)), 1)
    salary = int(np.clip(np.random.normal(72000, 28000), 34000, 220000))
    job_sat = np.random.choice([1, 2, 3, 4], p=[.14, .21, .32, .33])
    engagement = np.random.choice([1, 2, 3, 4], p=[.12, .22, .36, .30])
    wlb = np.random.choice([1, 2, 3, 4], p=[.10, .22, .40, .28])
    overtime = np.random.choice(["Yes", "No"], p=[.26, .74])
    last_promo = round(float(np.clip(
                 np.random.exponential(2.2), 0, tenure)), 1)
    perf = np.random.choice([2, 3, 4], p=[.10, .72, .18])
    work_mode = np.random.choice(
                ["On-site", "Hybrid", "Remote"], p=[.45, .42, .13])

    # News & Content structurally higher attrition
    # Evening shifts, breaking news pressure
    # Anomaly detection will surface this later
    dept_stress = 0.10 if dept == "News & Content" else 0.0

    risk = (
        (job_sat <= 2) * 0.15
        + (engagement <= 2) * 0.14
        + (overtime == "Yes") * 0.13
        + (wlb == 1) * 0.11
        + (salary < 45000) * 0.14
        + (tenure <= 1.5) * 0.16
        + (last_promo > 3) * 0.09
        + dept_stress
        + np.random.normal(0, 0.07)
    )
    attrition = "Yes" if risk > 0.38 else "No"

    rows.append({
        "EmployeeID": emp_id,
        "Age": age,
        "Department": dept,
        "JobRole": role,
        "TenureYears": tenure,
        "AnnualSalary": salary,
        "JobSatisfaction": job_sat,
        "EngagementScore": engagement,
        "WorkLifeBalance": wlb,
        "OverTime": overtime,
        "YearsSinceLastPromotion": last_promo,
        "PerformanceRating": perf,
        "WorkMode": work_mode,
        "Attrition": attrition,
    })

df = pd.DataFrame(rows)
df.to_csv("data/hris_export.csv", index=False)

print(f"Employees: {len(df)}")
print(f"Attrition rate: {(df['Attrition']=='Yes').mean():.1%}")
print(f"\nDept breakdown:\n{df['Department'].value_counts()}")
print(f"\nSample:\n{df.head(3)}")