import pandas as pd, glob, datetime
ts=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
out=f"reports/daily_health_checks/{ts}_DB_Health_Report.xlsx"

writer = pd.ExcelWriter(out, engine="openpyxl")

for csvfile in glob.glob("reports/daily_health_checks/*_tablespace.csv"):
    pd.read_csv(csvfile).to_excel(writer, sheet_name="tablespace", index=False)
for csvfile in glob.glob("reports/daily_health_checks/*_sessions.csv"):
    pd.read_csv(csvfile).to_excel(writer, sheet_name="sessions", index=False)
for csvfile in glob.glob("reports/daily_health_checks/*_top_sql.csv"):
    pd.read_csv(csvfile).to_excel(writer, sheet_name="top_sql", index=False)
for csvfile in glob.glob("reports/daily_health_checks/*_summary.csv"):
    pd.read_csv(csvfile).to_excel(writer, sheet_name="summary", index=False)

writer.close()
print("Consolidated report:", out)
