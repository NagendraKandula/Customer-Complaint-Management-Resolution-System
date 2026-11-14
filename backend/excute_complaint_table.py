
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, unquote

import pg8000.dbapi
import sqlparse
from dotenv import load_dotenv


# Load environment variables from backend/.env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing in .env")


def get_connection():
    """Connect to Neon PostgreSQL using pg8000."""

    parsed = urlparse(DATABASE_URL)

    connection = pg8000.dbapi.connect(
        user=unquote(parsed.username),
        password=unquote(parsed.password),
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip("/"),
        ssl_context=True
    )

    return connection


def execute_sql_file(cursor, file_path):
    """Read and execute SQL statements from a file."""

    print(f"\nExecuting: {file_path.name}")

    sql_content = file_path.read_text(encoding="utf-8")
    statements = sqlparse.split(sql_content)

    executed = 0

    for statement in statements:
        if statement.strip():
            cursor.execute(statement)
            executed += 1

    print(f"Successfully executed {executed} SQL statements.")


def main():
    sql_file = BASE_DIR / "database" / "03_complaint_table.sql"

    if not sql_file.exists():
        print(f"SQL file not found: {sql_file}")
        sys.exit(1)

    connection = None

    try:
        print("Connecting to Neon PostgreSQL...")

        connection = get_connection()
        cursor = connection.cursor()

        print("Database connection successful!")

        execute_sql_file(cursor, sql_file)

        connection.commit()

        print("\nMaster tables created successfully!")

    except Exception as error:
        if connection:
            connection.rollback()

        print("\nExecution failed!")
        print("Error:", error)

    finally:
        if connection:
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()
