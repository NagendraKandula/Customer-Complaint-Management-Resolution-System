
from data_generation.db_connection import get_connection

from data_generation.generators.status_history_generator import (
    run_status_history_generation,
)


def main():

    connection = get_connection()

    try:

        run_status_history_generation(connection)

    finally:

        connection.close()


if __name__ == "__main__":
    main()
