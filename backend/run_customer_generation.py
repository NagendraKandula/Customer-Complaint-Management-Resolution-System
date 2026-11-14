
from data_generation.db_connection import get_connection
from data_generation.generators.customer_generator import (
    run_customer_generation,
)


def main():
    connection = None

    try:
        connection = get_connection()

        run_customer_generation(connection)

    except Exception as error:
        print("Customer generation error:", error)

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
