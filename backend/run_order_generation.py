
from data_generation.db_connection import get_connection
from data_generation.generators.order_generator import (
    run_order_generation,
)


def main():
    connection = None

    try:
        connection = get_connection()
        run_order_generation(connection)

    except Exception as error:
        print("Order generation error:", error)

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
