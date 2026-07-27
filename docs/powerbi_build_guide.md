cat > docs/powerbi_build_guide.md << 'EOF'
# Power BI Build Guide

## Data Model
Star schema — attrition_scored as central fact table.

Relationships:
- attrition_scored[Department] -> anomaly_flags[Department]
  (many-to-one)
- hire_source_effectiveness -> attrition_scored
  (auto-detected on HireSource)

Standalone tables (no relationship needed):
- shap_feature_importance (feeds SHAP bar chart directly)
- turnover_by_tenure (pre-aggregated summary)
- ticket_vs_attrition (pre-aggregated summary)

## DAX Measures
Headcount = COUNTROWS(attrition_scored)

Attrition Rate =
DIVIDE(
  CALCULATE(COUNTROWS(attrition_scored),
  attrition_scored[Attrition] = "Yes"),
  [Headcount]
)

High Risk Count =
CALCULATE(COUNTROWS(attrition_scored),
attrition_scored[RiskSegment] = "High")

Avg Risk Score = AVERAGE(attrition_scored[AttritionRiskScore])

## Pages
Page 1 - Executive Summary: KPI cards, attrition by dept,
risk segment donut, department slicer

Page 2 - Attrition Drivers: SHAP importance bar, salary vs
risk scatter, avg risk by tenure band

Page 3 - Anomaly Detection: dept table with AnomalyFlag
conditional formatting, attrition by hire source,
ticket volume vs attrition

## Automation Architecture
Production: Power BI Service + scheduled refresh from
Snowflake. Pipeline runs at 2am, data updated, Power BI
refreshes at 6am. Leaders see current data at 9am.
Email = notification only, never the report itself.
EOF