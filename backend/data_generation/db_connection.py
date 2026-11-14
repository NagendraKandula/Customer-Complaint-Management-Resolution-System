
import os
from pathlib import Path
from urllib.parse import urlparse, unquote

import pg8000.dbapi
from dotenv import load_dotenv


# Load .env from backend directory
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError(
            "DATABASE_URL not found. Check your backend/.env file."
        )

    parsed = urlparse(database_url)

    if not all([parsed.hostname, parsed.username, parsed.password]):
        raise ValueError("DATABASE_URL is incomplete.")

    connection = pg8000.dbapi.connect(
        user=unquote(parsed.username),
        password=unquote(parsed.password),
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=unquote(parsed.path.lstrip("/")),
        ssl_context=True
    )

    return connection


def test_connection():
    connection = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT version();")
        result = cursor.fetchone()

        print("Connected to Neon successfully!")
        print("PostgreSQL version:", result[0])

        return True

    except Exception as error:
        print("Database connection failed!")
        print("Error:", error)

        return False

    finally:
        if connection:
            connection.close()
