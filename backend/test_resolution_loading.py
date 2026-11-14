
from data_generation.db_connection import get_connection
from data_generation.generators.resolution_generator import (
    load_resolution_reference_data,
)


def main():
    connection = get_connection()

    try:
        complaints = load_resolution_reference_data(connection)

        print("Eligible complaints:", len(complaints))

        for complaint in complaints[:5]:
            print(complaint)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
