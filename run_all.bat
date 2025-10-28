@echo off
call "C:\Users\samra\OneDrive\Desktop\db_automation\.venv\Scripts\activate.bat"
python "C:\Users\samra\OneDrive\Desktop\db_automation\automation\health_check.py"
python "C:\Users\samra\OneDrive\Desktop\db_automation\automation\email_alerts.py"
python "C:\Users\samra\OneDrive\Desktop\db_automation\automation\report_generator.py"
"C:\Users\samra\OneDrive\Desktop\db_automation\automation\backup_oracle.bat"

