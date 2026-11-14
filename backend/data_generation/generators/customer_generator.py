
from data_generation.config import (
    DATASET_SIZE,
    SCALE,
    START_DATE,
    END_DATE,
    BATCH_SIZE,
)

from data_generation.random_utils import (
    random_name,
    random_email,
    random_phone,
    random_boolean,
    random_datetime,
    random_weighted_choice,
)

from data_generation.id_generator import id_generator


# Customer tier distribution
CUSTOMER_TIER_DISTRIBUTION = {
    "STANDARD": 0.60,
    "SILVER": 0.22,
    "GOLD": 0.13,
    "PLATINUM": 0.05,
}


# Percentage of customers with missing contact information
EMAIL_MISSING_PROBABILITY = 0.02
PHONE_MISSING_PROBABILITY = 0.03

# Synthetic vulnerable-customer proportion
VULNERABLE_PROBABILITY = 0.08


def generate_customer_records():
    """
    Generate synthetic customer records in memory.
    Does not insert anything into the database.
    """

    total_customers = round(
        DATASET_SIZE["customers"] * SCALE
    )

    customers = []

    for _ in range(total_customers):

        customer_id = id_generator.customer_id()

        full_name = random_name()

        # Some customers may not have an email address
        email = (
            None
            if random_boolean(EMAIL_MISSING_PROBABILITY)
            else f"{customer_id.lower()}@example.com"
        )

        # Some customers may not have a phone number
        phone = (
            None
            if random_boolean(PHONE_MISSING_PROBABILITY)
            else random_phone()
        )

        customer_tier = random_weighted_choice(
            CUSTOMER_TIER_DISTRIBUTION
        )

        is_vulnerable = random_boolean(
            VULNERABLE_PROBABILITY
        )

        created_at = random_datetime(
            START_DATE,
            END_DATE
        )

        customers.append((
            customer_id,
            full_name,
            email,
            phone,
            customer_tier,
            is_vulnerable,
            created_at,
        ))

    return customers



def insert_customers(connection, customers):
    """
    Insert customer records using multi-row INSERT statements.
    """

    cursor = connection.cursor()

    columns = 7

    try:
        print("Checking existing customer records...", flush=True)

        cursor.execute("SELECT COUNT(*) FROM customers")
        existing_count = cursor.fetchone()[0]

        print("Existing customers:", existing_count, flush=True)

        if existing_count > 0:
            raise RuntimeError(
                f"Customers table already contains {existing_count} "
                "records. Refusing to insert duplicates."
            )

        total = len(customers)

        for start in range(0, total, BATCH_SIZE):

            batch = customers[start:start + BATCH_SIZE]

            # Generate placeholders for all rows in this batch
            row_placeholder = "(" + ", ".join(["%s"] * columns) + ")"

            placeholders = ", ".join(
                [row_placeholder] * len(batch)
            )

            insert_query = f"""
                INSERT INTO customers (
                    customer_id,
                    full_name,
                    email,
                    phone,
                    customer_tier,
                    is_vulnerable,
                    created_at
                )
                VALUES {placeholders}
            """

            # Flatten records into one parameter list
            parameters = [
                value
                for customer in batch
                for value in customer
            ]

            cursor.execute(insert_query, parameters)

            print(
                f"Inserted {min(start + len(batch), total)} "
                f"/ {total} customers",
                flush=True
            )

        connection.commit()

        print("\nCustomer data inserted successfully!")
        print("Total customers:", total)

    except Exception:
        connection.rollback()
        print("Customer insertion failed. Transaction rolled back.")
        raise

    finally:
        cursor.close()


def run_customer_generation(connection):
    """
    Complete customer generation workflow.
    """

    print("Generating customer records...")

    customers = generate_customer_records()

    print("Generated records:", len(customers))

    insert_customers(connection, customers)
