
from data_generation.db_connection import get_connection
from data_generation.generators.message_generator import (
    run_message_generation,
)


def main():

    connection = get_connection()

    try:
        run_message_generation(connection)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
