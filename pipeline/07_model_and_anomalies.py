"""
Attrition model + SHAP + risk segments + anomaly detection + API alert
Output: output/attrition_scored.csv
        output/shap_feature_importance.csv
        output/anomaly_flags.csv
"""
import pandas as pd
import numpy as np
import requests
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import shap

HEADERS = {"X-API-Key": "tegna-hr-api-key-2026"}
df = pd.read_csv("output/analytics_ready.csv")

cat_cols = ["Department", "JobRole", "OverTime",
            "WorkMode", "HireSource", "MatchStatus"]
X = df.drop(columns=["EmployeeID", "CandidateID", "HireDate", "Attrition"])
y = (df["Attrition"] == "Yes").astype(int)

for col in cat_cols:
    X[col] = LabelEncoder().fit_transform(X[col].astype(str))

# Stratified split preserves attrition ratio in both sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

# Class weighting — without this model predicts "stays" for everyone
scale_pos = (y_train==0).sum() / (y_train==1).sum()

model = xgb.XGBClassifier(
    n_estimators=300, max_depth=4, learning_rate=0.05,
    scale_pos_weight=scale_pos,
    random_state=42, eval_metric="logloss")
model.fit(X_train, y_train)

# ROC-AUC: overall discrimination
probs_test = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, probs_test)
print(f"ROC-AUC: {auc:.3f}")

# Precision@top-K: the business metric
# HR only acts on a limited group — this tells us how reliable
# the model is for the people it flags highest
K = int(0.15 * len(y_test))
top_k = np.argsort(probs_test)[-K:]
prec_k = y_test.values[top_k].mean()
print(f"Precision@top-15%: {prec_k:.1%}")

# SHAP — why is each person flagged
explainer = shap.TreeExplainer(model)
shap_vals  = explainer.shap_values(X_test)
importance = pd.DataFrame({
    "Feature": X_test.columns,
    "MeanAbsSHAP": np.abs(shap_vals).mean(axis=0),
}).sort_values("MeanAbsSHAP", ascending=False)

importance.to_csv("output/shap_feature_importance.csv", index=False)
print(f"\nTop 5 attrition drivers:")
print(importance.head().to_string(index=False))

# Risk segments on all employees
all_probs = model.predict_proba(X)[:, 1]
df["AttritionRiskScore"] = all_probs
df["RiskSegment"] = pd.cut(
    all_probs, bins=[0, 0.33, 0.66, 1.0],
    labels=["Low", "Medium", "High"])
df.to_csv("output/attrition_scored.csv", index=False)
print(f"\nRisk segments:\n{df['RiskSegment'].value_counts()}")

# Anomaly detection — dept z-scores
# Both signals elevated = real pattern, not noise
dept = df.groupby("Department").agg(
    Headcount=("EmployeeID","count"),
    AttritionRate=("Attrition", lambda s: (s=="Yes").mean()),
    AvgEngagement=("EngagementScore","mean"),
    AvgTickets=("TicketCount","mean"),
    HighRiskCount=("RiskSegment", lambda s: (s=="High").sum()),
).reset_index()

for col in ["AttritionRate", "AvgTickets"]:
    dept[f"{col}_z"] = (dept[col] - dept[col].mean()) / dept[col].std()

dept["AnomalyFlag"] = (
    (dept["AttritionRate_z"] > 0.8) &
    (dept["AvgTickets_z"] > 0.8))
dept.to_csv("output/anomaly_flags.csv", index=False)

print(f"\nDept anomaly summary:")
print(dept[["Department","AttritionRate","AvgTickets","AnomalyFlag"]]
      .round(3).to_string(index=False))

# Send alert via API for flagged departments
# In production: posts to Microsoft Teams HR channel
flagged_depts = dept[dept["AnomalyFlag"] == True]
for _, row in flagged_depts.iterrows():
    try:
        r = requests.post(
            "http://127.0.0.1:5000/api/alerts/anomaly",
            headers=HEADERS,
            json={"department": row["Department"],
                  "attrition_rate": row["AttritionRate"],
                  "avg_tickets": row["AvgTickets"]})
        print(f"\nAlert sent for: {row['Department']}")
    except Exception:
        print(f"Alert skipped (server not running): {row['Department']}")