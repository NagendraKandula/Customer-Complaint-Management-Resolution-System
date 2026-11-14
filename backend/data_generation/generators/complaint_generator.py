
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from ..db_connection import get_connection
from ..config import DATASET_SIZE, END_DATE, BATCH_SIZE
from ..random_utils import (
    random_choice,
    random_boolean,
    random_datetime,
    random_weighted_choice,
)
from ..id_generator import id_generator


# ---------------------------------------------------------
# 1. Complaint category distribution
# ---------------------------------------------------------

CATEGORY_DISTRIBUTION = {
    "PRODUCT_QUALITY": 0.15,
    "PRODUCT_SAFETY": 0.05,
    "DELIVERY_DELAY": 0.15,
    "ORDER_NOT_RECEIVED": 0.12,
    "PAYMENT_FAILURE": 0.10,
    "REFUND_DELAY": 0.10,
    "DAMAGED_PRODUCT": 0.10,
    "RETURN_REPLACEMENT": 0.08,
    "TECHNICAL_ISSUE": 0.08,
    "CUSTOMER_DISSATISFACTION": 0.07,
}

CHANNELS = [
    "EMAIL", "PHONE", "WEBSITE",
    "MOBILE_APP", "LIVE_CHAT", "SOCIAL_MEDIA"
]

SENTIMENTS = ["NEGATIVE", "VERY_NEGATIVE", "NEUTRAL"]

COMPLAINT_TEXTS = {
    "PRODUCT_QUALITY": [
        "The product quality is not as expected.",
        "The product stopped working after a few days.",
        "I am disappointed with the quality of this product.",
    ],
    "PRODUCT_SAFETY": [
        "The product overheated during normal usage.",
        "I noticed a potential safety issue with this product.",
        "The product produced smoke while operating.",
    ],
    "DELIVERY_DELAY": [
        "My order has not arrived on the expected date.",
        "The delivery is delayed without an update.",
        "I need an update about my delayed order.",
    ],
    "ORDER_NOT_RECEIVED": [
        "The order shows delivered but I have not received it.",
        "I have not received my order.",
        "The delivery status is incorrect.",
    ],
    "PAYMENT_FAILURE": [
        "My payment failed but the amount was deducted.",
        "I am facing an issue while completing payment.",
        "The payment transaction is not reflecting correctly.",
    ],
    "REFUND_DELAY": [
        "My refund has not been credited yet.",
        "The refund is taking longer than expected.",
        "Please provide an update on my pending refund.",
    ],
    "DAMAGED_PRODUCT": [
        "The product arrived in a damaged condition.",
        "The package was damaged when it arrived.",
        "I received a broken product.",
    ],
    "RETURN_REPLACEMENT": [
        "I want to return this product.",
        "I requested a replacement but have not received it.",
        "Please help me with the return process.",
    ],
    "TECHNICAL_ISSUE": [
        "I am unable to use the application.",
        "The website is showing an unexpected error.",
        "The application is not working correctly.",
    ],
    "CUSTOMER_DISSATISFACTION": [
        "I am unhappy with the service I received.",
        "I have contacted support multiple times without a solution.",
        "The overall customer experience was disappointing.",
    ],
}


# ---------------------------------------------------------
# 2. Load reference and transactional data
# ---------------------------------------------------------

def load_generation_data(cursor):

    cursor.execute("""
        SELECT
            o.order_id,
            o.customer_id,
            o.order_value,
            o.order_status,
            o.delivered_but_not_received,
            o.order_date,
            oi.product_id,
            p.is_safety_critical,
            c.is_vulnerable
        FROM orders o
        JOIN customers c
            ON c.customer_id = o.customer_id
        JOIN order_items oi
            ON oi.order_id = o.order_id
        JOIN products p
            ON p.product_id = oi.product_id
        ORDER BY o.order_id
    """)

    order_rows = cursor.fetchall()

    orders = defaultdict(list)

    for row in order_rows:
        (
            order_id,
            customer_id,
            order_value,
            order_status,
            delivered_not_received,
            order_date,
            product_id,
            safety_critical,
            vulnerable,
        ) = row

        orders[order_id].append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_value": float(order_value),
            "order_status": order_status,
            "delivered_not_received": delivered_not_received,
            "order_date": order_date,
            "product_id": product_id,
            "is_safety_critical": safety_critical,
            "is_vulnerable": vulnerable,
        })

    cursor.execute("""
        SELECT
            category_id,
            category_name,
            base_severity,
            is_safety
        FROM complaint_categories
        WHERE is_active = TRUE
    """)

    categories = {
        row[1]: {
            "category_id": row[0],
            "category_name": row[1],
            "base_severity": row[2],
            "is_safety": row[3],
        }
        for row in cursor.fetchall()
    }

    cursor.execute("""
        SELECT
            priority_rule_id,
            rule_name,
            priority_level,
            priority_score
        FROM priority_rules
        WHERE is_active = TRUE
    """)

    rules = {
        row[1]: {
            "priority_rule_id": row[0],
            "priority_level": row[2],
            "priority_score": row[3],
        }
        for row in cursor.fetchall()
    }

    return orders, categories, rules


# ---------------------------------------------------------
# 3. Select category and matching priority rule
# ---------------------------------------------------------

def select_priority_rule(
    category_name,
    category,
    order,
    is_repeat,
):

    # Higher-precedence rules are checked first.

    if category["is_safety"]:
        return "PRODUCT_SAFETY_OVERRIDE"

    if category["base_severity"] == "CRITICAL":
        return "CRITICAL_SEVERITY"

    if order["is_vulnerable"]:
        return "VULNERABLE_CUSTOMER"

    if is_repeat:
        return "REPEAT_COMPLAINT"

    if order["order_value"] >= 50000:
        return "HIGH_VALUE_ORDER"

    category_rules = {
        "ORDER_NOT_RECEIVED": "ORDER_NOT_RECEIVED",
        "PAYMENT_FAILURE": "PAYMENT_FAILURE",
        "REFUND_DELAY": "REFUND_DELAY",
        "PRODUCT_QUALITY": "PRODUCT_QUALITY",
        "DELIVERY_DELAY": "DELIVERY_DELAY",
        "TECHNICAL_ISSUE": "TECHNICAL_ISSUE",
        "DAMAGED_PRODUCT": "PRODUCT_QUALITY",
        "RETURN_REPLACEMENT": "PRODUCT_QUALITY",
        "CUSTOMER_DISSATISFACTION": "GENERAL_DISSATISFACTION",
    }

    return category_rules[category_name]


# ---------------------------------------------------------
# 4. Generate complaint records
# ---------------------------------------------------------

def generate_complaint_records(orders, categories, rules):

    total_complaints = DATASET_SIZE["complaints"]

    complaint_records = []

    # Used to identify earlier complaints from the same
    # customer and category.
    previous_complaints = defaultdict(list)

    available_orders = list(orders.values())

    for _ in range(total_complaints):

        order_items = random_choice(available_orders)
        order = random_choice(order_items)

        category_name = random_weighted_choice(
            CATEGORY_DISTRIBUTION
        )

        category = categories[category_name]

        customer_id = order["customer_id"]

        # A complaint may not need an order reference.
        # Keep order references for most complaints.
        order_id = order["order_id"]

        if category_name in (
            "PAYMENT_FAILURE",
            "TECHNICAL_ISSUE",
            "CUSTOMER_DISSATISFACTION",
        ) and random_boolean(0.20):
            order_id = None

        # Only create repeat complaints if an earlier
        # complaint exists for this customer/category.
        previous_key = (customer_id, category_name)

        possible_previous = previous_complaints[previous_key]

        is_repeat = (
            bool(possible_previous)
            and random_boolean(0.08)
        )

        repeat_of = None

        if is_repeat:
            repeat_of = random_choice(possible_previous)

        # Generate a timestamp after the order date.
        start_date = order["order_date"].date()

        end_date = datetime.strptime(
            END_DATE, "%Y-%m-%d"
        ).date()

        if start_date >= end_date:
            created_at = datetime.combine(
                end_date,
                datetime.min.time(),
                tzinfo=timezone.utc,
            )
        else:
            created_at = random_datetime(
                start_date.strftime("%Y-%m-%d"),
                END_DATE,
            )

        # Repeat complaints must happen after their
        # original complaint.
        if is_repeat:
            previous_time = next(
                record["created_at"]
                for record in complaint_records
                if record["complaint_id"] == repeat_of
            )

            created_at = max(
                created_at,
                previous_time + timedelta(minutes=1),
            )

        severity = category["base_severity"]

        rule_name = select_priority_rule(
            category_name,
            category,
            order,
            is_repeat,
        )

        rule = rules[rule_name]

        complaint_id = id_generator.complaint_id()

        complaint_text = random_choice(
            COMPLAINT_TEXTS[category_name]
        )

        status = random_choice([
            "OPEN",
            "CLASSIFIED",
            "ASSIGNED",
            "IN_PROGRESS",
            "WAITING_FOR_CUSTOMER",
        ])

        complaint = {
            "complaint_id": complaint_id,
            "customer_id": customer_id,
            "order_id": order_id,
            "product_id": order["product_id"],
            "category_id": category["category_id"],
            "priority_rule_id": rule["priority_rule_id"],
            "complaint_text": complaint_text,
            "channel": random_choice(CHANNELS),
            "sentiment": random_choice(SENTIMENTS),
            "severity": severity,
            "priority": rule["priority_level"],
            "priority_score": rule["priority_score"],
            "class_rule_fired": rule_name,
            "is_safety_related": category["is_safety"],
            "is_repeat": is_repeat,
            "repeat_of_complaint_id": repeat_of,
            "status": status,
            "reopen_count": 0,
            "closed_at": None,
            "created_at": created_at,
            "updated_at": created_at,
        }

        complaint_records.append(complaint)

        # Only completed records become candidates for
        # future repeat complaints.
        previous_complaints[previous_key].append(
            complaint_id
        )

    return complaint_records


# ---------------------------------------------------------
# 5. Insert records in batches
# ---------------------------------------------------------

def insert_complaints(cursor, records):

    columns = [
        "complaint_id",
        "customer_id",
        "order_id",
        "product_id",
        "category_id",
        "priority_rule_id",
        "complaint_text",
        "channel",
        "sentiment",
        "severity",
        "priority",
        "priority_score",
        "class_rule_fired",
        "is_safety_related",
        "is_repeat",
        "repeat_of_complaint_id",
        "status",
        "reopen_count",
        "closed_at",
        "created_at",
        "updated_at",
    ]

    column_sql = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    for start in range(0, len(records), BATCH_SIZE):

        batch = records[start:start + BATCH_SIZE]

        values_sql = ", ".join(
            [f"({placeholders})"] * len(batch)
        )

        query = f"""
            INSERT INTO complaints ({column_sql})
            VALUES {values_sql}
        """

        parameters = []

        for record in batch:
            parameters.extend(
                record[column] for column in columns
            )

        cursor.execute(query, tuple(parameters))

        print(
            f"Inserted {min(start + len(batch), len(records))}"
            f" / {len(records)} complaints"
        )


# ---------------------------------------------------------
# 6. Main runner
# ---------------------------------------------------------

def run_complaint_generation():

    print("Loading orders, categories and priority rules...")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM complaints")
        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            print(
                f"Complaints already exist: {existing_count}. "
                "Skipping generation to prevent duplicates."
            )
            return

        orders, categories, rules = load_generation_data(cursor)

        print(f"Orders available: {len(orders)}")
        print(f"Categories available: {len(categories)}")
        print(f"Priority rules available: {len(rules)}")

        if not orders:
            raise ValueError("No orders available.")

        if len(categories) != 10:
            raise ValueError("Expected 10 active complaint categories.")

        if len(rules) != 12:
            raise ValueError("Expected 12 active priority rules.")

        print("Generating complaint records...")

        records = generate_complaint_records(
            orders,
            categories,
            rules,
        )

        print(f"Generated complaints: {len(records)}")

        insert_complaints(cursor, records)

        connection.commit()

        cursor.execute("SELECT COUNT(*) FROM complaints")
        total = cursor.fetchone()[0]

        print("Complaint generation completed!")
        print(f"Total complaints in database: {total}")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
