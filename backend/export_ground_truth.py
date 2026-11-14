
import csv
from data_generation.db_connection import get_connection

connection = get_connection()

try:
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            ground_truth_id,
            entity_name,
            record_id,
            issue_type,
            expected_value,
            actual_value,
            expected_detection,
            scenario_name,
            notes
        FROM gt.ground_truth
        WHERE issue_type <> 'BASELINE'
        ORDER BY ground_truth_id
    """)

    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]

    with open("ground_truth.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"Exported {len(rows)} ground-truth records.")

    cursor.close()

finally:
    connection.close()
