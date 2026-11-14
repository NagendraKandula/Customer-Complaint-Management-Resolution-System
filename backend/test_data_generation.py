
from data_generation.config import DATASET_SIZE, SCALE, SEED
from data_generation.random_utils import (
    random_name,
    random_email,
    random_integer,
)
from data_generation.id_generator import id_generator
from data_generation.db_connection import test_connection


def main():
    print("Testing data generation foundation...\n")

    print("Seed:", SEED)
    print("Scale:", SCALE)
    print("Configured customers:", DATASET_SIZE["customers"])

    print("\nTesting Faker:")
    print("Name:", random_name())
    print("Email:", random_email())
    print("Random number:", random_integer(1, 100))

    print("\nTesting IDs:")
    print("Customer:", id_generator.customer_id())
    print("Order:", id_generator.order_id())
    print("Complaint:", id_generator.complaint_id())

    print("\nTesting Neon connection:")
    test_connection()


if __name__ == "__main__":
    main()
