
import csv
from pathlib import Path

from data_generation.db_connection import get_connection

# Project root/output folder
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output" / "generated_data"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TABLES = [
    "customers",
    "products",
    "orders",
    "order_items",
    "complaints",
    "complaint_messages",
    "complaint_assignments",
    "complaint_status_history",
    "resolutions",
    "sla_clocks",
    "sla_events",
    "surveys",
]

connection = get_connection()

try:
    cursor = connection.cursor()

    for table in TABLES:
        cursor.execute(f'SELECT * FROM public."{table}"')
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        output_file = OUTPUT_DIR / f"{table}.csv"

        with open(output_file, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(columns)
            writer.writerows(rows)

        print(f"Exported {table}: {len(rows)} rows")

    cursor.close()

finally:
    connection.close()

print("CSV export completed.")
