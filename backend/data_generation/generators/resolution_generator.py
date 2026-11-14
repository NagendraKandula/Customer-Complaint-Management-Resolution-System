from decimal import Decimal
from data_generation.random_utils import (
    random_choice, random_weighted_choice, random_decimal
)
from data_generation.id_generator import id_generator
from data_generation.generators.order_generator import insert_records


def load_resolution_reference_data(connection):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT c.complaint_id, c.status, cc.category_name,
               COALESCE(o.order_value, 0), h.resolved_at,
               ca.agent_id
        FROM complaints c
        JOIN complaint_categories cc ON c.category_id = cc.category_id
        JOIN (
            SELECT complaint_id, MIN(changed_at) AS resolved_at
            FROM complaint_status_history
            WHERE new_status = 'RESOLVED'
            GROUP BY complaint_id
        ) h ON c.complaint_id = h.complaint_id
        LEFT JOIN orders o ON c.order_id = o.order_id
        LEFT JOIN complaint_assignments ca
            ON c.complaint_id = ca.complaint_id
            AND ca.ended_at IS NULL
        WHERE c.status IN ('RESOLVED', 'CLOSED', 'REOPENED')
        ORDER BY c.complaint_id
    """)
    rows = cursor.fetchall()
    cursor.close()
    return rows


OPTIONS = {
    "REFUND_DELAY": ["REFUND", "EXPLANATION"],
    "DAMAGED_PRODUCT": ["REPLACEMENT", "REFUND"],
    "PRODUCT_QUALITY": ["REPLACEMENT", "REFUND", "REPAIR"],
    "DELIVERY_DELAY": ["REDELIVERY", "REFUND"],
    "ORDER_NOT_RECEIVED": ["REDELIVERY", "REFUND"],
    "PAYMENT_FAILURE": ["REFUND", "EXPLANATION"],
    "RETURN_REPLACEMENT": ["REFUND", "REPLACEMENT"],
    "TECHNICAL_ISSUE": ["REPAIR", "EXPLANATION"],
    "PRODUCT_SAFETY": ["REFUND", "REPLACEMENT"],
    "CUSTOMER_DISSATISFACTION": ["EXPLANATION", "REFUND"],
}


def generate_resolution(row):
    complaint_id, status, category, order_value, resolved_at, agent_id = row

    resolution_type = random_choice(OPTIONS[category])
    outcome = random_weighted_choice({
        "RESOLVED": 0.85, "PARTIAL": 0.15
    })

    refund = None
    if resolution_type == "REFUND":
        refund = order_value
        if outcome == "PARTIAL":
            refund = refund * Decimal(str(random_decimal(0.25, 0.75)))

    return (
        id_generator.resolution_id(complaint_id, 1),
        complaint_id, 1, resolution_type, outcome,
        f"{resolution_type} for {category}",
        agent_id, resolved_at,
        round(refund, 2) if refund is not None else None,
        status != "REOPENED"
    )


def run_resolution_generation(connection):
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM resolutions")
        if cursor.fetchone()[0] != 0:
            raise ValueError("Resolutions table is not empty")

        rows = load_resolution_reference_data(connection)
        if len(rows) != 1012:
            raise ValueError(f"Expected 1012 complaints, got {len(rows)}")

        records = [generate_resolution(row) for row in rows]

        insert_records(
            connection, "resolutions",
            ["resolution_id", "complaint_id", "cycle_no",
             "resolution_type", "outcome", "resolution_notes", "resolved_by",
             "resolved_at", "refund_amount", "is_final"],
            records
        )

        connection.commit()
        print("Resolutions inserted:", len(records))

    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
