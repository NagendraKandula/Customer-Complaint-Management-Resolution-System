
from datetime import timedelta

from data_generation.config import (
    DATASET_SIZE,
    SCALE,
    BATCH_SIZE,
)

from data_generation.random_utils import (
    random_choice,
    random_integer,
)

from data_generation.id_generator import id_generator

from data_generation.generators.order_generator import insert_records


# Exactly three messages per complaint.
MESSAGES_PER_COMPLAINT = 3


# Customer messages based on complaint category.
CUSTOMER_MESSAGES = {
    "PRODUCT_QUALITY": [
        "The product quality is not as expected. I am disappointed.",
        "I noticed a problem with the quality of the product.",
        "The product does not work as described. Please help.",
    ],
    "PRODUCT_SAFETY": [
        "I noticed a potential safety issue while using this product.",
        "The product appears unsafe. Please investigate immediately.",
        "I am concerned about a safety problem with this product.",
    ],
    "DELIVERY_DELAY": [
        "My order has been delayed. Please provide an update.",
        "I have been waiting for my order. When will it arrive?",
        "The delivery is taking longer than expected.",
    ],
    "ORDER_NOT_RECEIVED": [
        "My order shows delivered, but I have not received it.",
        "I have not received my order. Please investigate.",
        "The package is missing. Please help me locate it.",
    ],
    "PAYMENT_FAILURE": [
        "My payment failed, but the amount appears to have been deducted.",
        "I am facing an issue while completing my payment.",
        "The payment transaction was unsuccessful. Please check.",
    ],
    "REFUND_DELAY": [
        "I have not received my refund yet. Please check.",
        "My refund is still pending. Please provide an update.",
        "It has been several days, and my refund has not arrived.",
    ],
    "DAMAGED_PRODUCT": [
        "The product arrived damaged. I need assistance.",
        "I received a damaged item. Please arrange a replacement.",
        "The package arrived, but the product is broken.",
    ],
    "RETURN_REPLACEMENT": [
        "I would like to return this product.",
        "Please help me arrange a replacement.",
        "I am requesting a return for my recent purchase.",
    ],
    "TECHNICAL_ISSUE": [
        "I am experiencing a technical problem with the service.",
        "The application is not working as expected.",
        "I am unable to complete the operation because of a technical issue.",
    ],
    "CUSTOMER_DISSATISFACTION": [
        "I am unhappy with the overall experience.",
        "I am disappointed with the service I received.",
        "Please look into my issue. I am not satisfied.",
    ],
}


# Agent acknowledgement templates.
AGENT_MESSAGES = [
    "We have received your complaint and are looking into the issue.",
    "Thank you for contacting us. Our team is reviewing your concern.",
    "We apologize for the inconvenience. We will investigate this matter.",
    "Your complaint has been registered. We will keep you updated.",
]


# Customer follow-up templates.
FOLLOW_UP_MESSAGES = [
    "Thank you. Please resolve this as soon as possible.",
    "I appreciate the update. Please keep me informed.",
    "I am waiting for a resolution. Please update me.",
    "Please let me know once this issue is resolved.",
]


# System-generated update templates.
SYSTEM_MESSAGES = [
    "Complaint acknowledgement notification generated.",
    "Complaint status update notification generated.",
    "The complaint has been registered successfully.",
]


def load_message_reference_data(connection):
    """
    Load complaints, categories and agents from PostgreSQL.
    """

    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT
                c.complaint_id,
                c.customer_id,
                c.channel,
                c.created_at,
                cc.category_name
            FROM complaints c
            JOIN complaint_categories cc
                ON c.category_id = cc.category_id
            ORDER BY c.complaint_id
        """)

        complaints = [
            {
                "complaint_id": row[0],
                "customer_id": row[1],
                "channel": row[2],
                "created_at": row[3],
                "category_name": row[4],
            }
            for row in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT agent_id
            FROM agents
            WHERE is_active = TRUE
            ORDER BY agent_id
        """)

        agents = [
            row[0] for row in cursor.fetchall()
        ]

        if not complaints:
            raise ValueError(
                "No complaints found. Generate complaints first."
            )

        if not agents:
            raise ValueError(
                "No active agents found."
            )

        return complaints, agents

    finally:
        cursor.close()

def generate_message_records(complaints, agents):
    """
    Generate three chronological messages per complaint.
    """

    messages = []

    for complaint in complaints:

        complaint_id = complaint["complaint_id"]
        customer_id = complaint["customer_id"]
        category = complaint["category_name"]
        channel = complaint["channel"]
        created_at = complaint["created_at"]

        # Select one active agent.
        agent_id = random_choice(agents)

        # Message 1: Customer submits complaint.
        first_message_id = id_generator.message_id(
            complaint_id
        )

        messages.append((
            first_message_id,
            complaint_id,
            "CUSTOMER",
            customer_id,
            random_choice(CUSTOMER_MESSAGES[category]),
            channel,
            created_at,
        ))

        # Message 2: Agent acknowledges complaint.
        agent_message_id = id_generator.message_id(
            complaint_id
        )

        agent_time = created_at + timedelta(
            minutes=random_integer(5, 120)
        )

        messages.append((
            agent_message_id,
            complaint_id,
            "AGENT",
            agent_id,
            random_choice(AGENT_MESSAGES),
            channel,
            agent_time,
        ))

        # Message 3: Customer follow-up or system update.
        final_message_id = id_generator.message_id(
            complaint_id
        )

        final_sender_type = random_choice([
            "CUSTOMER",
            "SYSTEM",
        ])

        if final_sender_type == "CUSTOMER":
            final_sender_id = customer_id
            final_message_text = random_choice(
                FOLLOW_UP_MESSAGES
            )
        else:
            final_sender_id = None
            final_message_text = random_choice(
                SYSTEM_MESSAGES
            )

        final_time = agent_time + timedelta(
            minutes=random_integer(5, 240)
        )

        messages.append((
            final_message_id,
            complaint_id,
            final_sender_type,
            final_sender_id,
            final_message_text,
            channel,
            final_time,
        ))

    return messages

def run_message_generation(connection):

    print("Loading complaints and agents...", flush=True)

    complaints, agents = load_message_reference_data(
        connection
    )

    print("Complaints available:", len(complaints))
    print("Agents available:", len(agents))

    expected_messages = round(
        DATASET_SIZE["messages"] * SCALE
    )

    expected_complaints = round(
        DATASET_SIZE["complaints"] * SCALE
    )

    if len(complaints) != expected_complaints:
        raise ValueError(
            f"Expected {expected_complaints} complaints, "
            f"found {len(complaints)}."
        )

    if expected_messages != (
        len(complaints) * MESSAGES_PER_COMPLAINT
    ):
        raise ValueError(
            "Message target must equal three messages "
            "per complaint in this generator version."
        )

    print("\nGenerating message records...", flush=True)

    records = generate_message_records(
        complaints,
        agents
    )

    print("Generated messages:", len(records))

    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT COUNT(*) FROM complaint_messages"
        )

        existing_messages = cursor.fetchone()[0]

        if existing_messages > 0:
            raise RuntimeError(
                "Messages already exist. "
                "Refusing duplicate insertion."
            )

        insert_records(
            connection,
            "complaint_messages",
            [
                "message_id",
                "complaint_id",
                "sender_type",
                "sender_id",
                "message_text",
                "channel",
                "sent_at",
            ],
            records
        )

        connection.commit()

        print("\nMessage generation completed!")
        print("Total messages:", len(records))

    except Exception:
        connection.rollback()
        print("Message insertion failed. Transaction rolled back.")
        raise

    finally:
        cursor.close()
