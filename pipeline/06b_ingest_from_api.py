import requests
import pandas as pd

BASE = "http://127.0.0.1:5000"

def call_api(endpoint, params=None):
    url = f"{BASE}{endpoint}"
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        print("ERROR: API server not running.")
        print("Run in Terminal 1: python pipeline/00_api_server.py")
        raise

print("Pulling from UKG Pro API...")
ukg  = call_api("/api/ukg/employees")
hris = pd.DataFrame(ukg["data"])
print(f"  Received: {ukg['total_records']} employees")

print("Pulling from Greenhouse API...")
gh  = call_api("/api/greenhouse/candidates")
ats = pd.DataFrame(gh["data"])
print(f"  Received: {gh['total_records']} candidates")

print("Pulling hiring sources from Greenhouse...")
hs = call_api("/api/greenhouse/hiring-sources")
hiring_sources = pd.DataFrame(hs["data"])
print(f"  Received: {len(hiring_sources)} source categories")

print("Pulling from ServiceNow API...")
sn      = call_api("/api/servicenow/summary")
tickets = pd.DataFrame(sn["data"])
print(f"  Received: {len(tickets)} employees with tickets")

hris.to_csv("data/hris_export.csv", index=False)
ats.to_csv("data/ats_export.csv", index=False)
tickets.to_csv("data/tickets_from_api.csv", index=False)

print("\nAll systems polled successfully")
print(f"UKG Pro:    {len(hris)} rows staged")
print(f"Greenhouse: {len(ats)} rows staged")
print(f"ServiceNow: {len(tickets)} rows staged")