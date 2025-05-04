# 🛠️ Reflash Master

A Python script that connects to a SQL Server database, identifies devices that failed an update 3+ times, resets their retry flags, and logs/export the changes.

---

🔧 **Features**

✅ SQL Server Connection via `pyodbc`  
✅ Retry Logic Reset – Clears `NoOfTries` and `Failed` flags for matching records  
✅ CSV Export – Outputs affected device IDs to `/exports`  
✅ Logging – Tracks all actions in timestamped `/logs`  
✅ Cleanup – Keeps only the 5 most recent log and CSV files  

---

📂 **Technologies Used**

- Python 🐍
- `pyodbc` (SQL Server DB access)
- `dotenv` (secure environment variable loading)
- `csv` and `os` (file handling)
- `logging` (audit trail)
- `glob` (pattern-based file cleanup)

---

🔐 **Environment Variables Required** (via `.env` file):

