"""
Loads all source CSVs into MySQL (MAMP)
"""
import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine(
    "mysql+pymysql://root:root@127.0.0.1:8889/people_analytics"
)

tables = {
    "hris":      "data/hris_export.csv",
    "ats":       "data/ats_export.csv",
    "cases":     "data/case_log.csv",
    "id_bridge": "data/id_bridge.csv",
}

for table_name, filepath in tables.items():
    df = pd.read_csv(filepath)
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False
    )
    with engine.connect() as conn:
        count = conn.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).fetchone()[0]
    print(f"Loaded {table_name}: {count} rows")

print("\nAll tables loaded into MySQL.")
print("Open Workbench -> people_analytics to see them visually")