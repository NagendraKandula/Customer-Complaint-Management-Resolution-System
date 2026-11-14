
from data_generation.db_connection import get_connection

TABLES = [
    "complaints",
    "customers",
    "categories",
    "agents",
    "teams",
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
        print(f"\n{'=' * 50}")
        print(f"TABLE: {table}")
        print("=" * 50)

        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = %s
            ORDER BY ordinal_position
        """, (table,))

        columns = cursor.fetchall()

        if not columns:
            print("Table not found in public schema")
            continue

        for column in columns:
            print(
                f"{column[0]} | "
                f"{column[1]} | "
                f"Nullable: {column[2]}"
            )

    cursor.close()

finally:
    connection.close()
