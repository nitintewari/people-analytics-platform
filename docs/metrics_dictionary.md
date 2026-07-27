cat > docs/metrics_dictionary.md << 'EOF'
# People Metrics Data Dictionary

## Headcount
Active employees as of the last day of the period.
Excludes contractors and interns.

## Turnover Rate
Separations in period divided by average headcount.
Reported as:
- Voluntary: employee-initiated resignations
- Involuntary: terminations and layoffs
- Regretted: voluntary separations the org wanted to prevent

## Attrition Risk Score
Model-predicted probability (0-1) that an active employee
separates voluntarily within 6 months.
Segmented: High (>0.66), Medium (0.33-0.66), Low (<0.33)
Access: HR partners only — never shown to people managers
at individual level without HR partner review.

## Engagement Score
Survey response on 1-4 scale.
Minimum group size of 5 before reporting at department level
to prevent identification of individuals.

## Time to Hire
Days from requisition approval to offer acceptance.
Median reported, not mean — outlier searches skew averages.

## HR Case Volume
Tickets opened per employee per period from ServiceNow.
Used as leading indicator of disengagement — reviewed
alongside attrition and engagement, never in isolation.
EOF