import pyodbc
import logging
import csv
from datetime import datetime
from dotenv import load_dotenv
import os
import glob

# --- Load environment variables ---
load_dotenv()

server = os.getenv("DB_SERVER")
database = os.getenv("DB_DATABASE")
username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

update_version = ''

# --- Create output folders ---
os.makedirs('logs', exist_ok=True)
os.makedirs('exports', exist_ok=True)

# --- Generate timestamped file names ---
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join('logs', f'update_reset_{timestamp}.log')
csv_filename = os.path.join('exports', f'updated_devices_{timestamp}.csv')

# --- Setup logging ---
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def clean_old_files(directory, pattern, keep=5):
    files = sorted(glob.glob(os.path.join(directory, pattern)), key=os.path.getmtime, reverse=True)
    for old_file in files[keep:]:
        try:
            os.remove(old_file)
            logging.info(f"Removed old file: {old_file}")
        except Exception as e:
            logging.warning(f"Failed to remove {old_file}: {e}")

def reset_retry_states():
    try:
        conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};DATABASE={database};UID={username};PWD={password}'
        )
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            logging.info(f"Checking for devices with update version '{update_version}' to reset...")

            select_sql = """
                SELECT ID FROM [dbo].[Device_Update_List]
                WHERE Update_version = ?
                  AND NoOfTries >= 3
                  AND Failed = 1
            """
            cursor.execute(select_sql, update_version)
            rows = cursor.fetchall()
            updated_ids = [row.ID for row in rows]

            if not updated_ids:
                logging.info(f"No matching devices found for reset with update version '{update_version}'.")
                return

            logging.info(f"Found {len(updated_ids)} device(s) to reset for update version '{update_version}'.")

            # Export to CSV
            with open(csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['DeviceID'])
                for device_id in updated_ids:
                    writer.writerow([device_id])
            logging.info(f"Exported updated device IDs to '{csv_filename}'.")

            # Perform the update
            update_sql = """
                UPDATE [dbo].[Device_Update_List]
                SET NoOfTries = 0,
                    Failed = 0
                WHERE Update_version = ?
                  AND NoOfTries >= 3
                  AND Failed = 1
            """
            cursor.execute(update_sql, update_version)
            conn.commit()
            logging.info(f"Updated {cursor.rowcount} row(s) for update version '{update_version}'.")

    except Exception as e:
        logging.error(f"Error occurred during update for version '{update_version}': {e}")

if __name__ == "__main__":
    reset_retry_states()
    clean_old_files('logs', 'update_reset_*.log', keep=5)
    clean_old_files('exports', 'updated_devices_*.csv', keep=5)