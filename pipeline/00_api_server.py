from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

hris_data  = pd.read_csv("data/hris_export.csv")
ats_data   = pd.read_csv("data/ats_export.csv")
cases_data = pd.read_csv("data/case_log.csv")

@app.route("/api/ukg/employees", methods=["GET"])
def get_employees():
    dept   = request.args.get("department")
    status = request.args.get("attrition")
    df = hris_data.copy()
    if dept:   df = df[df["Department"] == dept]
    if status: df = df[df["Attrition"] == status]
    return jsonify({
        "source": "UKG Pro",
        "total_records": len(df),
        "data": df.to_dict(orient="records")
    })

@app.route("/api/greenhouse/candidates", methods=["GET"])
def get_candidates():
    dept = request.args.get("department")
    df = ats_data.copy()
    if dept: df = df[df["Department"] == dept]
    return jsonify({
        "source": "Greenhouse",
        "total_records": len(df),
        "data": df.to_dict(orient="records")
    })

@app.route("/api/greenhouse/hiring-sources", methods=["GET"])
def get_hiring_sources():
    summary = (ats_data
        .groupby("HireSource")
        .agg(Count=("CandidateID","count"),
             AvgTimeToHire=("TimeToHireDays","mean"))
        .reset_index().round(1)
        .to_dict(orient="records"))
    return jsonify({"source": "Greenhouse", "data": summary})

@app.route("/api/servicenow/cases", methods=["GET"])
def get_cases():
    df = cases_data.copy()
    return jsonify({
        "source": "ServiceNow",
        "total_records": len(df),
        "data": df.to_dict(orient="records")
    })

@app.route("/api/servicenow/summary", methods=["GET"])
def get_case_summary():
    summary = (cases_data
        .groupby("Email")
        .agg(TicketCount=("TicketCategory","count"),
             EscalatedCount=("Escalated","sum"),
             AvgResolveDays=("DaysToResolve","mean"))
        .reset_index().round(2)
        .to_dict(orient="records"))
    return jsonify({"source": "ServiceNow", "data": summary})

@app.route("/api/alerts/anomaly", methods=["POST"])
def send_anomaly_alert():
    data = request.json
    dept = data.get("department")
    rate = data.get("attrition_rate")
    print(f"\n*** ALERT: {dept} — attrition {float(rate):.1%} ***\n")
    return jsonify({
        "alert_sent": True,
        "department": dept,
        "channel": "Microsoft Teams — HR Leadership"
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    print("="*50)
    print("Mock HR API Server — port 5000")
    print("="*50)
    app.run(debug=True, port=5000)