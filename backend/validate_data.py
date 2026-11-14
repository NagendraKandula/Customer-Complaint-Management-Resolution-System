
from pathlib import Path
from data_generation.db_connection import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

report = []

def log(message):
    print(message)
    report.append(message)


def check_count(cursor, query):
    cursor.execute(query)
    return cursor.fetchone()[0]


connection = get_connection()

try:
    cursor = connection.cursor()

    log("CUSTOMER COMPLAINT SYSTEM - VALIDATION REPORT")
    log("=" * 55)

    # 1. Primary key constraints
    log("\n1. PRIMARY KEY VALIDATION")

    cursor.execute("""
        SELECT table_name, constraint_name
        FROM information_schema.table_constraints
        WHERE constraint_type = 'PRIMARY KEY'
          AND table_schema = 'public'
        ORDER BY table_name
    """)

    pk_constraints = cursor.fetchall()

    for table, constraint in pk_constraints:
        log(f"PASS: {table} has primary key ({constraint})")

    # 2. Foreign key constraints
    log("\n2. FOREIGN KEY VALIDATION")

    cursor.execute("""
        SELECT table_name, constraint_name
        FROM information_schema.table_constraints
        WHERE constraint_type = 'FOREIGN KEY'
          AND table_schema = 'public'
        ORDER BY table_name
    """)

    fk_constraints = cursor.fetchall()

    for table, constraint in fk_constraints:
        log(f"PASS: {table} has foreign key ({constraint})")

    # 3. Required data checks
    log("\n3. REQUIRED DATA VALIDATION")

    checks = [
        ("Customers", "SELECT COUNT(*) FROM customers WHERE customer_id IS NULL"),
        ("Products", "SELECT COUNT(*) FROM products WHERE product_id IS NULL"),
        ("Orders", "SELECT COUNT(*) FROM orders WHERE order_id IS NULL"),
        ("Complaints", "SELECT COUNT(*) FROM complaints WHERE complaint_id IS NULL"),
        ("Resolutions", "SELECT COUNT(*) FROM resolutions WHERE resolution_id IS NULL"),
    ]

    for name, query in checks:
        count = check_count(cursor, query)
        log(f"{'PASS' if count == 0 else 'FAIL'}: {name} missing IDs = {count}")

    # 4. Allowed complaint values
    log("\n4. ALLOWED VALUE VALIDATION")

    invalid_status = check_count(cursor, """
        SELECT COUNT(*)
        FROM complaints
        WHERE status NOT IN (
            'OPEN', 'CLASSIFIED', 'ASSIGNED',
            'IN_PROGRESS', 'WAITING_FOR_CUSTOMER',
            'ESCALATED', 'RESOLVED', 'CLOSED', 'REOPENED'
        )
    """)

    invalid_priority = check_count(cursor, """
        SELECT COUNT(*)
        FROM complaints
        WHERE priority NOT IN ('P1', 'P2', 'P3', 'P4')
    """)

    log(f"{'PASS' if invalid_status == 0 else 'FAIL'}: Invalid complaint statuses = {invalid_status}")
    log(f"{'PASS' if invalid_priority == 0 else 'FAIL'}: Invalid priorities = {invalid_priority}")

    # 5. Lifecycle validation
    log("\n5. LIFECYCLE VALIDATION")

    invalid_reopen = check_count(cursor, """
        SELECT COUNT(*)
        FROM complaints
        WHERE reopen_count < 0
    """)

    invalid_resolution = check_count(cursor, """
        SELECT COUNT(*)
        FROM resolutions r
        JOIN complaints c ON c.complaint_id = r.complaint_id
        WHERE r.resolved_at < c.created_at
    """)

    log(f"{'PASS' if invalid_reopen == 0 else 'FAIL'}: Negative reopen counts = {invalid_reopen}")
    log(f"{'PASS' if invalid_resolution == 0 else 'FAIL'}: Resolution before complaint = {invalid_resolution}")

    # 6. Ground truth validation
    log("\n6. GROUND TRUTH VALIDATION")

    anomaly_count = check_count(cursor, """
        SELECT COUNT(*)
        FROM gt.ground_truth
        WHERE issue_type <> 'BASELINE'
          AND expected_detection = TRUE
    """)

    log(f"{'PASS' if anomaly_count == 6 else 'FAIL'}: Known anomalies = {anomaly_count} (expected 6)")

    # 7. Record counts
    log("\n7. GENERATED RECORD COUNTS")

    tables = [
        "customers", "products", "orders", "order_items",
        "complaints", "complaint_messages",
        "complaint_assignments", "complaint_status_history",
        "resolutions", "sla_clocks", "sla_events", "surveys"
    ]

    for table in tables:
        count = check_count(cursor, f'SELECT COUNT(*) FROM public."{table}"')
        log(f"{table}: {count} rows")

    log("\nVALIDATION COMPLETED")

    cursor.close()

finally:
    connection.close()

with open(OUTPUT_DIR / "validation_report.txt", "w", encoding="utf-8") as file:
    file.write("\n".join(report))

print("\nReport saved to output/validation_report.txt")
