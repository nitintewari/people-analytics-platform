cat > docs/governance.md << 'EOF'
# Data Governance

## Principles
People data is sensitive by default. Trust in the numbers
and protection of the people behind them are both structural,
not procedural.

## Access Tiers

**Tier 1 — All leaders:**
Aggregated metrics — headcount, turnover rates,
engagement by department (minimum group size: 5).

**Tier 2 — HR partners only:**
Individual risk segments and drivers.
Used for intervention planning with HR partner oversight.

**Tier 3 — Restricted (pipeline only):**
Compensation detail and identity crosswalk (name/email/ID).
Excluded from analytics-ready table entirely.
Never reaches any dashboard or report output.

## Quality Controls
- Identity joins validated using fuzzy name matching
- Low-confidence matches flagged for review, never dropped
- Every run produces data_quality_report.csv as audit trail
- One analytics-ready table feeds all reporting
- Numbers cannot diverge between reports

## Model Governance
- Risk scores are decision support, not decisions
- Interventions require HR partner review
- Drivers surfaced via SHAP for full explainability
- Model performance logged per run

## Flag Never Drop
Bad records go to quality report — never silently deleted
or auto-corrected. A human always makes the final call
on data that affects a real person.
EOF