
from data_generation.db_connection import get_connection
from data_generation.generators.product_generator import (
    run_product_generation,
)


def main():
    connection = None

    try:
        connection = get_connection()
        run_product_generation(connection)

    except Exception as error:
        print("Product generation error:", error)

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
