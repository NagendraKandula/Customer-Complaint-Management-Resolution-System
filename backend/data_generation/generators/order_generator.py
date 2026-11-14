
from datetime import timedelta

from data_generation.config import (
    DATASET_SIZE,
    SCALE,
    START_DATE,
    END_DATE,
    BATCH_SIZE,
)

from data_generation.random_utils import (
    random_integer,
    random_boolean,
    random_datetime,
    random_weighted_choice,
    random_sample,
)

from data_generation.id_generator import id_generator


ORDER_STATUS_DISTRIBUTION = {
    "DELIVERED": 0.55,
    "SHIPPED": 0.15,
    "PLACED": 0.10,
    "CANCELLED": 0.08,
    "RETURNED": 0.07,
    "LOST": 0.05,
}


def load_reference_data(connection):
    """
    Load existing customers and products from PostgreSQL.
    We use actual database IDs instead of assuming their sequence.
    """

    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT customer_id
            FROM customers
            ORDER BY customer_id
        """)

        customers = [
            row[0] for row in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT product_id, unit_price
            FROM products
            ORDER BY product_id
        """)

        products = [
            {
                "product_id": row[0],
                "unit_price": row[1],
            }
            for row in cursor.fetchall()
        ]

        if not customers:
            raise ValueError("No customers found. Generate customers first.")

        if not products:
            raise ValueError("No products found. Generate products first.")

        return customers, products

    finally:
        cursor.close()


def generate_order_records(customers, products):
    """
    Generate orders and their corresponding order items.

    Returns:
        orders: list of order records
        order_items: list of order-item records
    """

    total_orders = round(
        DATASET_SIZE["orders"] * SCALE
    )

    orders = []
    order_items = []

    for _ in range(total_orders):

        # Generate order ID
        order_id = id_generator.order_id()

        # Select an existing customer
        customer_id = random_sample(customers, 1)[0]

        # Generate order date and timestamp
        created_at = random_datetime(
            START_DATE,
            END_DATE
        )

        order_date = created_at.date()

        # Choose order status
        order_status = random_weighted_choice(
            ORDER_STATUS_DISTRIBUTION
        )

        # Delivery date depends on the order status
        delivery_date = None

        if order_status in ("DELIVERED", "RETURNED"):
            delivery_date = (
                order_date
                + timedelta(days=random_integer(1, 10))
            )

        # A small number of delivered orders have a delivery dispute
        delivered_but_not_received = (
            order_status == "DELIVERED"
            and random_boolean(0.015)
        )

        # Select 1 to 4 different products
        item_count = random_integer(
            1,
            min(4, len(products))
        )

        selected_products = random_sample(
            products,
            item_count
        )

        order_number = int(order_id[-6:])

        order_value = 0

        for item_number, product in enumerate(
            selected_products,
            start=1
        ):

            quantity = random_integer(1, 3)

            unit_price = product["unit_price"]

            # Keep exact decimal arithmetic from PostgreSQL
            line_total = unit_price * quantity

            order_value += line_total

            order_item_id = id_generator.order_item_id(
                order_number,
                item_number
            )

            order_items.append((
                order_item_id,
                order_id,
                product["product_id"],
                quantity,
                unit_price,
                line_total,
            ))

        orders.append((
            order_id,
            customer_id,
            order_date,
            order_value,
            order_status,
            delivered_but_not_received,
            delivery_date,
            created_at,
        ))

    return orders, order_items


def insert_records(connection, table_name, columns, records):
    """
    Reusable multi-row INSERT function.
    """

    if not records:
        return

    cursor = connection.cursor()

    try:
        column_count = len(columns)

        column_names = ", ".join(columns)

        for start in range(0, len(records), BATCH_SIZE):

            batch = records[start:start + BATCH_SIZE]

            row_placeholder = "(" + ", ".join(
                ["%s"] * column_count
            ) + ")"

            placeholders = ", ".join(
                [row_placeholder] * len(batch)
            )

            query = f"""
                INSERT INTO {table_name} ({column_names})
                VALUES {placeholders}
            """

            parameters = [
                value
                for record in batch
                for value in record
            ]

            cursor.execute(query, parameters)

            print(
                f"{table_name}: "
                f"{min(start + len(batch), len(records))}"
                f" / {len(records)} inserted",
                flush=True
            )

    finally:
        cursor.close()


def run_order_generation(connection):
    """
    Complete order-generation workflow.
    """

    print("Loading customers and products...", flush=True)

    customers, products = load_reference_data(connection)

    print("Customers available:", len(customers))
    print("Products available:", len(products))

    print("\nGenerating orders...", flush=True)

    orders, order_items = generate_order_records(
        customers,
        products
    )

    print("Generated orders:", len(orders))
    print("Generated order items:", len(order_items))

    cursor = connection.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM orders")
        existing_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM order_items")
        existing_items = cursor.fetchone()[0]

        if existing_orders > 0 or existing_items > 0:
            raise RuntimeError(
                "Orders or order_items already contain records. "
                "Refusing duplicate insertion."
            )

        # Both inserts happen in the same transaction.
        insert_records(
            connection,
            "orders",
            [
                "order_id",
                "customer_id",
                "order_date",
                "order_value",
                "order_status",
                "delivered_but_not_received",
                "delivery_date",
                "created_at",
            ],
            orders
        )

        insert_records(
            connection,
            "order_items",
            [
                "order_item_id",
                "order_id",
                "product_id",
                "quantity",
                "unit_price",
                "line_total",
            ],
            order_items
        )

        connection.commit()

        print("\nOrder data inserted successfully!")
        print("Total orders:", len(orders))
        print("Total order items:", len(order_items))

    except Exception:
        connection.rollback()
        print("Order insertion failed. Transaction rolled back.")
        raise

    finally:
        cursor.close()
