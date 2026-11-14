
import json
from datetime import date

from data_generation.db_connection import get_connection
from data_generation.random_utils import (
    random_name,
    random_email,
    random_integer,
)


# --------------------------------------------------
# 1. TEAMS
# --------------------------------------------------

TEAMS = [
    ("TEAM-01", "GENERAL_SUPPORT",
     "Handles general customer questions and complaints"),

    ("TEAM-02", "ORDER_SUPPORT",
     "Handles order tracking, delivery delays and missing orders"),

    ("TEAM-03", "PAYMENT_REFUND",
     "Handles payment failures and refund-related complaints"),

    ("TEAM-04", "PRODUCT_SAFETY",
     "Handles product safety incidents and critical risks"),

    ("TEAM-05", "TECHNICAL_SUPPORT",
     "Handles technical problems and application issues"),

    ("TEAM-06", "RETURNS_REPLACEMENT",
     "Handles returns, damaged products and replacements"),

    ("TEAM-07", "ESCALATION_TEAM",
     "Handles escalated and high-priority complaints"),

    ("TEAM-08", "CUSTOMER_RETENTION",
     "Handles customer dissatisfaction and retention"),
]


# --------------------------------------------------
# 2. COMPLAINT CATEGORIES
# --------------------------------------------------

CATEGORIES = [
    (
        "CAT-01", "PRODUCT_QUALITY",
        "General product quality and performance issues",
        "MEDIUM", False, "TEAM-01"
    ),
    (
        "CAT-02", "PRODUCT_SAFETY",
        "Product overheating, electrical hazards or physical injury",
        "CRITICAL", True, "TEAM-04"
    ),
    (
        "CAT-03", "DELIVERY_DELAY",
        "Orders delivered later than the expected date",
        "MEDIUM", False, "TEAM-02"
    ),
    (
        "CAT-04", "ORDER_NOT_RECEIVED",
        "Customer reports that an order was not received",
        "HIGH", False, "TEAM-02"
    ),
    (
        "CAT-05", "PAYMENT_FAILURE",
        "Payment failures, duplicate charges or transaction issues",
        "HIGH", False, "TEAM-03"
    ),
    (
        "CAT-06", "REFUND_DELAY",
        "Refund has not been received within the expected period",
        "MEDIUM", False, "TEAM-03"
    ),
    (
        "CAT-07", "DAMAGED_PRODUCT",
        "Product received in damaged or unusable condition",
        "HIGH", False, "TEAM-06"
    ),
    (
        "CAT-08", "RETURN_REPLACEMENT",
        "Return, exchange or replacement-related complaints",
        "MEDIUM", False, "TEAM-06"
    ),
    (
        "CAT-09", "TECHNICAL_ISSUE",
        "Website, mobile application or technical failures",
        "MEDIUM", False, "TEAM-05"
    ),
    (
        "CAT-10", "CUSTOMER_DISSATISFACTION",
        "General dissatisfaction with customer experience",
        "HIGH", False, "TEAM-08"
    ),
]


# --------------------------------------------------
# 3. PRIORITY RULES
# --------------------------------------------------

PRIORITY_RULES = [
    {
        "id": "PR-01",
        "name": "PRODUCT_SAFETY_OVERRIDE",
        "condition": {
            "field": "is_safety_related",
            "operator": "equals",
            "value": True
        },
        "priority": "P1",
        "score": 100
    },
    {
        "id": "PR-02",
        "name": "CRITICAL_SEVERITY",
        "condition": {
            "field": "severity",
            "operator": "equals",
            "value": "CRITICAL"
        },
        "priority": "P1",
        "score": 98
    },
    {
        "id": "PR-03",
        "name": "HIGH_VALUE_ORDER",
        "condition": {
            "field": "order_value",
            "operator": "greater_than_or_equal",
            "value": 1000
        },
        "priority": "P2",
        "score": 85
    },
    {
        "id": "PR-04",
        "name": "VULNERABLE_CUSTOMER",
        "condition": {
            "field": "customer_is_vulnerable",
            "operator": "equals",
            "value": True
        },
        "priority": "P1",
        "score": 95
    },
    {
        "id": "PR-05",
        "name": "REPEAT_COMPLAINT",
        "condition": {
            "field": "is_repeat",
            "operator": "equals",
            "value": True
        },
        "priority": "P2",
        "score": 80
    },
    {
        "id": "PR-06",
        "name": "ORDER_NOT_RECEIVED",
        "condition": {
            "field": "category",
            "operator": "equals",
            "value": "ORDER_NOT_RECEIVED"
        },
        "priority": "P2",
        "score": 78
    },
    {
        "id": "PR-07",
        "name": "PAYMENT_FAILURE",
        "condition": {
            "field": "category",
            "operator": "equals",
            "value": "PAYMENT_FAILURE"
        },
        "priority": "P2",
        "score": 75
    },
    {
        "id": "PR-08",
        "name": "REFUND_DELAY",
        "condition": {
            "field": "category",
            "operator": "equals",
            "value": "REFUND_DELAY"
        },
        "priority": "P3",
        "score": 60
    },
    {
        "id": "PR-09",
        "name": "PRODUCT_QUALITY",
        "condition": {
            "field": "category",
            "operator": "equals",
            "value": "PRODUCT_QUALITY"
        },
        "priority": "P3",
        "score": 55
    },
    {
        "id": "PR-10",
        "name": "DELIVERY_DELAY",
        "condition": {
            "field": "category",
            "operator": "equals",
            "value": "DELIVERY_DELAY"
        },
        "priority": "P3",
        "score": 50
    },
    {
        "id": "PR-11",
        "name": "TECHNICAL_ISSUE",
        "condition": {
            "field": "category",
            "operator": "equals",
            "value": "TECHNICAL_ISSUE"
        },
        "priority": "P3",
        "score": 45
    },
    {
        "id": "PR-12",
        "name": "GENERAL_DISSATISFACTION",
        "condition": {
            "field": "category",
            "operator": "equals",
            "value": "CUSTOMER_DISSATISFACTION"
        },
        "priority": "P4",
        "score": 40
    },
]


# --------------------------------------------------
# 4. SLA POLICIES
# --------------------------------------------------

SLA_POLICIES = [
    ("P1", 15, 240, 80),
    ("P2", 60, 480, 80),
    ("P3", 240, 1440, 80),
    ("P4", 480, 2880, 80),
]


# --------------------------------------------------
# 5. GENERATE TEAM ROWS
# --------------------------------------------------

def generate_team_rows():
    return [
        (team_id, team_name, description, True)
        for team_id, team_name, description in TEAMS
    ]


# --------------------------------------------------
# 6. GENERATE AGENT ROWS
# --------------------------------------------------

def generate_agent_rows():
    rows = []
    agent_number = 1

    for team_id, _, _ in TEAMS:
        for _ in range(5):
            agent_id = f"AGT-{agent_number:03d}"

            rows.append((
                agent_id,
                team_id,
                random_name(),
                random_email(),
                random_integer(15, 30),
                True
            ))

            agent_number += 1

    return rows


# --------------------------------------------------
# 7. GENERATE CATEGORY ROWS
# --------------------------------------------------

def generate_category_rows():
    return [
        (
            category_id,
            category_name,
            description,
            severity,
            is_safety,
            team_id,
            True
        )
        for (
            category_id,
            category_name,
            description,
            severity,
            is_safety,
            team_id
        ) in CATEGORIES
    ]


# --------------------------------------------------
# 8. GENERATE PRIORITY RULE ROWS
# --------------------------------------------------

def generate_priority_rule_rows():
    start_date = date(2025, 1, 1)
    end_date = date(2099, 12, 31)

    return [
        (
            rule["id"],
            rule["name"],
            json.dumps(rule["condition"]),
            rule["priority"],
            rule["score"],
            start_date,
            end_date,
            True
        )
        for rule in PRIORITY_RULES
    ]


# --------------------------------------------------
# 9. GENERATE SLA ROWS
# --------------------------------------------------

def generate_sla_rows():
    return SLA_POLICIES


# --------------------------------------------------
# 10. INSERT ALL MASTER DATA
# --------------------------------------------------

def insert_master_data(cursor):

    # Prevent accidental duplicate or partial insertion.
    tables = [
        "teams",
        "agents",
        "complaint_categories",
        "priority_rules",
        "sla_policy",
    ]

    existing_counts = {}

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        existing_counts[table] = cursor.fetchone()[0]

    non_empty = {
        table: count
        for table, count in existing_counts.items()
        if count > 0
    }

    if non_empty:
        raise RuntimeError(
            "Master tables are not empty. "
            f"Existing row counts: {non_empty}. "
            "Check the database before running this generator again."
        )

    # Insert teams first because agents and categories reference them.
    cursor.executemany(
        """
        INSERT INTO teams
        (team_id, team_name, description, is_active)
        VALUES (%s, %s, %s, %s)
        """,
        generate_team_rows()
    )

    # Insert agents.
    cursor.executemany(
        """
        INSERT INTO agents
        (agent_id, team_id, agent_name, email,
         max_open_complaints, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        generate_agent_rows()
    )

    # Insert complaint categories.
    cursor.executemany(
        """
        INSERT INTO complaint_categories
        (category_id, category_name, description,
         base_severity, is_safety, default_team_id, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        generate_category_rows()
    )

    # Insert priority rules.
    cursor.executemany(
        """
        INSERT INTO priority_rules
        (priority_rule_id, rule_name, condition_json,
         priority_level, priority_score,
         effective_from, effective_to, is_active)
        VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s, %s)
        """,
        generate_priority_rule_rows()
    )

    # Insert SLA policies.
    cursor.executemany(
        """
        INSERT INTO sla_policy
        (priority_level, response_minutes,
         resolution_minutes, escalation_threshold_pct)
        VALUES (%s, %s, %s, %s)
        """,
        generate_sla_rows()
    )


# --------------------------------------------------
# 11. MAIN EXECUTION FUNCTION
# --------------------------------------------------

def generate_master_data():

    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        insert_master_data(cursor)

        connection.commit()

        print("\nMaster data inserted successfully!")

        for table in [
            "teams",
            "agents",
            "complaint_categories",
            "priority_rules",
            "sla_policy",
        ]:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count}")

    except Exception:
        if connection:
            connection.rollback()

        raise

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    generate_master_data()
