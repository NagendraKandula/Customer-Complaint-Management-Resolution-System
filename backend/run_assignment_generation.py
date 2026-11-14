
from data_generation.db_connection import get_connection

from data_generation.generators.assignment_generator import (
    run_assignment_generation,
)


def main():

    connection = get_connection()

    try:
        run_assignment_generation(connection)

    finally:
        connection.close()


if __name__ == "__main__":
    main()
