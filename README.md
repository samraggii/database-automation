# 🧩 Oracle Database Automation & Monitoring System

### Independent Project | Built with Python, SQL, and Oracle 21c XE

This project simulates **Oracle Database Administration automation** using Python scripts and SQL procedures.  
It automates daily health checks, performance monitoring, replication simulation, and alerting — designed to demonstrate practical skills in **database performance optimization, automation, and reliability engineering.**

---

## 📁 Project Structure

```
db_automation/
│
├── automation/
│   ├── health_check.py          # Collects Oracle metrics (sessions, I/O, tablespace, SQL stats)
│   ├── generate_load.py         # Generates synthetic DB workload
│   ├── report_generator.py      # Exports metrics to Excel & CSV
│
├── sql/
│   ├── 01_schema_setup.sql      # Creates tables, indexes, constraints
│   ├── 02_load_sample_data.sql  # Populates sample customers, orders, products
│   ├── 03_workload.sql          # Sample workload to stress the DB
│   ├── 04_replication_simulation.sql # Trigger + scheduler job for replication
│
├── reports/
│   ├── logs/                    # Health check logs
│   ├── outputs/                 # CSV and Excel reports
│
├── config/
│   └── .env                     # Stores DB_USER, DB_PASSWORD, DB_DSN
│
├── requirements.txt             # Python dependencies
├── healthcare.db (optional)     # Example SQLite for testing locally
└── README.md                    # Documentation (this file)
```

---

## ⚙️ Installation & Setup

### 1️⃣ Prerequisites
- [Oracle Database 21c XE](https://www.oracle.com/database/technologies/appdev/xe.html)
- [Python 3.12+](https://www.python.org/downloads/)
- [SQL*Plus or SQL Developer](https://www.oracle.com/database/sqldeveloper/)
- Git (for cloning)

---

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/db_automation.git
cd db_automation
```

---

### 3️⃣ Create a Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scriptsctivate   # Windows
# or
source .venv/bin/activate  # macOS/Linux
```

---

### 4️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 5️⃣ Configure Environment Variables
Edit `config/.env` with your database credentials:
```
DB_USER=app_admin
DB_PASSWORD=YourPassword123
DB_DSN=localhost/XEPDB1
```

---

### 6️⃣ Initialize Oracle Schema
Connect with SQL*Plus and run:
```sql
ALTER SESSION SET CONTAINER = XEPDB1;
@sql/01_schema_setup.sql
@sql/02_load_sample_data.sql
```

---

### 7️⃣ Run Automation Scripts

**Run health checks:**
```bash
python automation/health_check.py
```

**Generate workload:**
```bash
python automation/generate_load.py
```

**Generate reports:**
```bash
python automation/report_generator.py
```

Logs and reports will appear under:
```
reports/logs/
reports/outputs/
```

---

## 🧠 Features

✅ **Automated Oracle Health Check** – Captures session count, tablespace usage, and top SQLs  
✅ **Performance Tuning Metrics** – Evaluates execution time and I/O stats under workload  
✅ **Replication Simulation** – Trigger + DBMS_SCHEDULER job that syncs changes into a replica table  
✅ **Email Alerting (optional)** – Python SMTP module sends notifications for CPU/memory thresholds  
✅ **Audit Logs** – Every run generates logs and report exports (CSV + Excel)  

---

## 📊 Sample Report Preview

> *(Screenshot Placeholder — upload your Excel report or log snapshot here)*

| Metric | Description | Sample Value |
|--------|--------------|--------------|
| Active Sessions | Count of active user sessions | 15 |
| Tablespace Usage | % utilization across tablespaces | 72.5% |
| Top SQL by Elapsed Time | Most expensive queries | SELECT * FROM ORDERS... |

---

## 🧩 Technologies Used

| Category | Tools |
|-----------|-------|
| Database | Oracle 21c XE |
| Programming | Python 3.12, SQL |
| Libraries | `oracledb`, `pandas`, `openpyxl`, `python-dotenv` |
| Reporting | CSV, Excel |
| OS/Env | Windows PowerShell + Virtual Environment |

---

## 🚀 Example Workflow

| Step | Action | Tool |
|------|---------|------|
| 1 | Run `01_schema_setup.sql` to create schema | SQL*Plus |
| 2 | Load data with `02_load_sample_data.sql` | SQL Developer |
| 3 | Execute `health_check.py` for metrics | Python |
| 4 | Stress-test using `generate_load.py` | Python |
| 5 | Re-run health check & report | Python |
| 6 | Verify replication via `orders_replica` | SQL Developer |

---

## 🧾 License

This project is released under the MIT License.  
You can freely modify and distribute it for educational or professional use.

---

## 👤 Author

**Samraggi Singh**  
Database & Systems Analyst (Independent Project)  
📍 University of Texas at Arlington | 💻 [LinkedIn](https://www.linkedin.com/in/samraggi-singh)

---

## ⭐ Acknowledgments

Special thanks to the Oracle Database Express Edition team for providing a lightweight local DB engine for automation prototyping.
