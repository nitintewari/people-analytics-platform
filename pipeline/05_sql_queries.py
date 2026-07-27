"""
SQL queries — saves results to both MySQL tables AND CSV files
MySQL tables: visible in Workbench
CSV files: feed Power BI and downstream scripts
"""
import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine(
    "mysql+pymysql://root:root@127.0.0.1:8889/people_analytics"
)

def run_and_save(query, table_name, csv_name, description):
    """
    Runs a SQL query, saves result to:
    1. MySQL table (visible in Workbench)
    2. CSV file (feeds Power BI)
    """
    print(f"\nRunning: {description}")
    df = pd.read_sql(query, engine)
    print(df.to_string(index=False))

    # Save to MySQL as a new table
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False
    )

    # Save to CSV
    df.to_csv(f"output/{csv_name}", index=False)
    print(f"Saved: MySQL table '{table_name}' + output/{csv_name}")
    return df

# Query 1: Overall turnover rate
run_and_save("""
SELECT
    COUNT(*) AS TotalEmployees,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END)
        AS TotalAttrition,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 2
    ) AS TurnoverRatePct
FROM hris
""", "report_turnover_overall", "turnover_overall.csv",
"Overall turnover rate")

# Query 2: Turnover by department
run_and_save("""
SELECT
    Department,
    COUNT(*) AS Headcount,
    SUM(CASE WHEN Attrition = 'Yes' THEN 1 ELSE 0 END)
        AS Attritions,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 2
    ) AS TurnoverRatePct
FROM hris
GROUP BY Department
ORDER BY TurnoverRatePct DESC
""", "report_turnover_by_dept", "dept_turnover.csv",
"Turnover rate by department")

# Query 3: Turnover by tenure band
run_and_save("""
SELECT
    CASE
        WHEN TenureYears < 1  THEN '0-1 years'
        WHEN TenureYears < 2  THEN '1-2 years'
        WHEN TenureYears < 5  THEN '2-5 years'
        WHEN TenureYears < 10 THEN '5-10 years'
        ELSE '10+ years'
    END AS TenureBand,
    COUNT(*) AS Headcount,
    ROUND(
        SUM(CASE WHEN Attrition = 'Yes' THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 2
    ) AS TurnoverRatePct
FROM hris
GROUP BY TenureBand
ORDER BY TurnoverRatePct DESC
""", "report_turnover_by_tenure", "turnover_by_tenure.csv",
"Turnover by tenure band")

# Query 4: Compensation analysis
run_and_save("""
SELECT
    Department,
    COUNT(*) AS Headcount,
    ROUND(MIN(AnnualSalary), 0)  AS MinSalary,
    ROUND(AVG(AnnualSalary), 0)  AS AvgSalary,
    ROUND(MAX(AnnualSalary), 0)  AS MaxSalary,
    ROUND(
        (MAX(AnnualSalary) - MIN(AnnualSalary))
        / MIN(AnnualSalary) * 100, 1
    ) AS SalaryRangePct
FROM hris
GROUP BY Department
ORDER BY AvgSalary DESC
""", "report_comp_analysis", "comp_analysis.csv",
"Compensation by department")

# Query 5: Engagement distribution
run_and_save("""
SELECT
    Department,
    ROUND(AVG(EngagementScore), 2) AS AvgEngagement,
    SUM(CASE WHEN EngagementScore <= 2 THEN 1 ELSE 0 END)
        AS LowEngagementCount,
    COUNT(*) AS Headcount,
    ROUND(
        SUM(CASE WHEN EngagementScore <= 2 THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 1
    ) AS LowEngagementPct
FROM hris
GROUP BY Department
ORDER BY LowEngagementPct DESC
""", "report_engagement", "engagement_by_dept.csv",
"Engagement by department")

# Query 6: Overtime analysis
run_and_save("""
SELECT
    Department,
    COUNT(*) AS Headcount,
    SUM(CASE WHEN OverTime = 'Yes' THEN 1 ELSE 0 END)
        AS OvertimeCount,
    ROUND(
        SUM(CASE WHEN OverTime = 'Yes' THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 1
    ) AS OvertimePct,
    ROUND(
        SUM(CASE WHEN OverTime = 'Yes' AND Attrition = 'Yes'
            THEN 1.0 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN OverTime = 'Yes'
            THEN 1 ELSE 0 END), 0) * 100, 1
    ) AS OvertimeAttritionPct
FROM hris
GROUP BY Department
ORDER BY OvertimePct DESC
""", "report_overtime", "overtime_by_dept.csv",
"Overtime by department")

# Query 7: Time to hire
run_and_save("""
SELECT
    h.Department,
    COUNT(*) AS Hires,
    ROUND(AVG(a.TimeToHireDays), 1) AS AvgDaysToHire,
    MIN(a.TimeToHireDays) AS MinDays,
    MAX(a.TimeToHireDays) AS MaxDays
FROM hris h
JOIN id_bridge b ON h.EmployeeID = b.EmployeeID
JOIN ats a ON b.CandidateID = a.CandidateID
GROUP BY h.Department
ORDER BY AvgDaysToHire DESC
""", "report_time_to_hire", "time_to_hire.csv",
"Time to hire by department")

# Query 8: Hire source effectiveness
run_and_save("""
SELECT
    a.HireSource,
    COUNT(*) AS TotalHires,
    SUM(CASE WHEN h.Attrition = 'Yes' THEN 1 ELSE 0 END)
        AS Attritions,
    ROUND(
        SUM(CASE WHEN h.Attrition = 'Yes' THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 2
    ) AS AttritionRatePct
FROM hris h
JOIN id_bridge b ON h.EmployeeID = b.EmployeeID
JOIN ats a ON b.CandidateID = a.CandidateID
GROUP BY a.HireSource
ORDER BY AttritionRatePct ASC
""", "report_hire_source", "hire_source_effectiveness.csv",
"Hire source effectiveness")

# Query 9: Promotion gap
run_and_save("""
SELECT
    Department,
    ROUND(AVG(YearsSinceLastPromotion), 2) AS AvgYearsSincePromo,
    SUM(CASE WHEN YearsSinceLastPromotion > 3 THEN 1 ELSE 0 END)
        AS StagnantCount,
    COUNT(*) AS Headcount,
    ROUND(
        SUM(CASE WHEN YearsSinceLastPromotion > 3
            THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 1
    ) AS StagnantPct
FROM hris
GROUP BY Department
ORDER BY StagnantPct DESC
""", "report_promotion_gap", "promotion_gap.csv",
"Promotion gap by department")

# Query 10: Ticket volume vs attrition (cross-system insight)
run_and_save("""
SELECT
    CASE
        WHEN t.TicketCount = 0 THEN '0 tickets'
        WHEN t.TicketCount BETWEEN 1 AND 3 THEN '1-3 tickets'
        WHEN t.TicketCount BETWEEN 4 AND 7 THEN '4-7 tickets'
        ELSE '8+ tickets'
    END AS TicketBand,
    COUNT(*) AS Employees,
    ROUND(
        SUM(CASE WHEN h.Attrition = 'Yes' THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 2
    ) AS AttritionRatePct
FROM hris h
LEFT JOIN (
    SELECT b.EmployeeID, COUNT(*) AS TicketCount
    FROM cases c
    JOIN id_bridge b ON c.Email = b.Email
    GROUP BY b.EmployeeID
) t ON h.EmployeeID = t.EmployeeID
GROUP BY TicketBand
ORDER BY AttritionRatePct DESC
""", "report_ticket_vs_attrition", "ticket_vs_attrition.csv",
"Ticket volume vs attrition")

print("\n" + "="*50)
print("ALL DONE")
print("="*50)
print("\nMySQL Workbench: refresh Tables to see report_ tables")
print("output/ folder: check CSVs for Power BI")