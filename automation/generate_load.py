# automation/generate_load.py
import os, time
import oracledb
from dotenv import load_dotenv

# Load .env from ../config/.env (relative to this file), override current env
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", ".env"))
load_dotenv(ENV_PATH, override=True)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

# Debug line (remove after it works)
print(f"[ENV] DB_USER={DB_USER!r} DB_DSN={DB_DSN!r} DB_PASSWORD_SET={bool(DB_PASSWORD)}  (from {ENV_PATH})")

if not DB_USER or not DB_PASSWORD or not DB_DSN:
    raise RuntimeError(
        f"Missing envs. Ensure {ENV_PATH} contains DB_USER, DB_PASSWORD, DB_DSN. "
        f"Got DB_USER={DB_USER!r}, DB_DSN={DB_DSN!r}, DB_PASSWORD_SET={bool(DB_PASSWORD)}"
    )

con = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
cur = con.cursor()

sql = """
SELECT c.city, COUNT(*) cnt
FROM orders o JOIN customers c ON o.customer_id=c.customer_id
WHERE o.order_ts >= SYSTIMESTAMP - INTERVAL '7' DAY
GROUP BY c.city
ORDER BY cnt DESC
"""

# Run for ~3 minutes to generate load
end = time.time() + 180
runs = 0
while time.time() < end:
    cur.execute(sql)
    cur.fetchall()
    runs += 1
print(f"Ran workload {runs} times.")

cur.close()
con.close()
