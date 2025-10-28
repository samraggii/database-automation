import os, datetime, csv, pandas as pd, yaml, logging
from dotenv import load_dotenv 
import oracledb

# --- load .env from config with absolute path ---
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", ".env"))
load_dotenv(ENV_PATH, override=True)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

# TEMP debug to confirm values are seen (remove after it works)
print(f"[ENV] DB_USER={DB_USER!r} DB_DSN={DB_DSN!r} DB_PASSWORD_SET={bool(DB_PASSWORD)}")

# Hard guard so you get a clear error if anything is missing
if not DB_USER or not DB_PASSWORD or not DB_DSN:
    raise RuntimeError(f"Missing envs. Expected in {ENV_PATH}. Got "f"DB_USER={DB_USER!r}, DB_DSN={DB_DSN!r}, DB_PASSWORD_SET={bool(DB_PASSWORD)}")

with open("config/thresholds.yaml") as f:
    TH = yaml.safe_load(f)

def query_rows(cur, sql):
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    return cols, cur.fetchall()

def main():
    os.makedirs("reports/daily_health_checks", exist_ok=True)
    os.makedirs("reports/logs", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    con = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    cur = con.cursor()

    # Tablespace utilization (requires SELECT on DBA views)
    q_tablespace = """
    SELECT df.tablespace_name, ROUND((df.total_mb - NVL(fs.free_mb,0)) / df.total_mb * 100,2) pct_used, df.total_mb, NVL(fs.free_mb,0) free_mb
    FROM (SELECT tablespace_name, SUM(bytes)/1024/1024 total_mb 
    FROM dba_data_files GROUP BY tablespace_name) df
    LEFT JOIN (SELECT tablespace_name, SUM(bytes)/1024/1024 free_mb
    FROM dba_free_space GROUP BY tablespace_name) fs
    ON df.tablespace_name = fs.tablespace_name
    ORDER BY pct_used DESC
    """
    # Active sessions
    q_sessions = "SELECT COUNT(*) active_sessions FROM v$session WHERE status='ACTIVE'"

    # Top SQL by elapsed time (fallback if v$sqlstats missing)
    q_sql = """
    SELECT * FROM (SELECT sql_id, executions, round(elapsed_time/1000) elapsed_ms, round(buffer_gets/DECODE(NULLIF(executions,0),0,1,executions)) gets_per_exec 
    FROM v$sqlarea
    WHERE executions > 0
    ORDER BY elapsed_time DESC
    ) WHERE ROWNUM <= 10
    """

    # Basic CPU/memory via v$osstat if available
    q_os = """
    SELECT stat_name, value FROM v$osstat
    WHERE stat_name IN ('NUM_CPUS','PHYSICAL_MEMORY_BYTES','LOAD','BUSY_TIME')
    """

    checks = {}
    for name, sql in [("tablespace", q_tablespace), ("sessions", q_sessions), ("top_sql", q_sql), ("os", q_os)]:
        try:
            cols, rows = query_rows(cur, sql)
            df = pd.DataFrame(rows, columns=cols)
            df.to_csv(f"reports/daily_health_checks/{ts}_{name}.csv", index=False)
            df.to_excel(f"reports/daily_health_checks/{ts}_{name}.xlsx", index=False)
            checks[name] = df
        except Exception as e:
            logging.error("Query %s failed: %s", name, e)

    # Evaluate thresholds
    alerts = []
    if "tablespace" in checks and not checks["tablespace"].empty:
        worst = checks["tablespace"]["PCT_USED"].max()
        if worst >= TH["tablespace_pct_used_crit"]:
            alerts.append(f"CRIT: Tablespace usage {worst}%")
        elif worst >= TH["tablespace_pct_used_warn"]:
            alerts.append(f"WARN: Tablespace usage {worst}%")

    if "sessions" in checks and not checks["sessions"].empty:
        active = int(checks["sessions"].iloc[0]["ACTIVE_SESSIONS"])
        if active >= TH["active_sessions_crit"]:
            alerts.append(f"CRIT: Active sessions {active}")
        elif active >= TH["active_sessions_warn"]:
            alerts.append(f"WARN: Active sessions {active}")

    # Approximate avg elapsed ms from top SQL sample
    if "top_sql" in checks and not checks["top_sql"].empty:
        avg_elapsed = checks["top_sql"]["ELAPSED_MS"].mean()
        if avg_elapsed >= TH["avg_sql_elapsed_ms_crit"]:
            alerts.append(f"CRIT: Avg top SQL elapsed {avg_elapsed:.0f} ms")
        elif avg_elapsed >= TH["avg_sql_elapsed_ms_warn"]:
            alerts.append(f"WARN: Avg top SQL elapsed {avg_elapsed:.0f} ms")

    # Persist a summary
    summary_path = f"reports/daily_health_checks/{ts}_summary.csv"
    with open(summary_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerow(["alerts_count", len(alerts)])
        for a in alerts:
            w.writerow(["alert", a])

    logging.info("Health check complete with %d alerts", len(alerts))
    print("| Summary | Alerts |")
    print(f"| {ts} | {len(alerts)} |")

if __name__ == "__main__":
    main()
