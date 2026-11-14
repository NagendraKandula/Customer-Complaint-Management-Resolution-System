
import os
from urllib.parse import urlparse, unquote

import pg8000
from dotenv import load_dotenv

print("Starting database connection test...")

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env")

else:
    try:
        # Parse Neon PostgreSQL connection URL
        parsed = urlparse(DATABASE_URL)

        connection = pg8000.dbapi.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip("/"),
            user=unquote(parsed.username),
            password=unquote(parsed.password),
            ssl_context=True
        )

        cursor = connection.cursor()

        cursor.execute("SELECT version();")
        result = cursor.fetchone()

        print("\nConnected to Neon successfully!")
        print("PostgreSQL version:", result[0])

        cursor.close()
        connection.close()

    except Exception as e:
        print("\nDatabase connection failed:")
        print(type(e).__name__, e)
