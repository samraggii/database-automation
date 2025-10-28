import os, smtplib, glob
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
SMTP=os.getenv("ALERTS_SMTP_HOST"); PORT=int(os.getenv("ALERTS_SMTP_PORT","587"))
FROM=os.getenv("ALERTS_EMAIL_FROM"); TO=os.getenv("ALERTS_EMAIL_TO")
USER=os.getenv("ALERTS_EMAIL_USER"); PASS=os.getenv("ALERTS_EMAIL_PASS")

def latest_summary():
    files = sorted(glob.glob("reports/daily_health_checks/*_summary.csv"))
    return files[-1] if files else None

def send_alert(body):
    msg = MIMEText(body)
    msg["Subject"]="DB ALERT: Health Check Thresholds Breached"
    msg["From"]=FROM; msg["To"]=TO
    with smtplib.SMTP(SMTP, PORT) as s:
        s.starttls()
        s.login(USER, PASS)
        s.send_message(msg)

if __name__=="__main__":
    sfile = latest_summary()
    if not sfile:
        print("No summary found.")
        raise SystemExit(0)
    with open(sfile) as f:
        content = f.read()
    # Alert if at least one "CRIT" or "WARN"
    if "CRIT:" in content or "WARN:" in content:
        send_alert(f"Thresholds exceeded.\n\n{content}")
        print("Alert sent.")
    else:
        print("No alerts.")
