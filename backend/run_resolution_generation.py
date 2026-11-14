from data_generation.db_connection import get_connection
from data_generation.generators.resolution_generator import run_resolution_generation

connection = get_connection()
try:
    run_resolution_generation(connection)
finally:
    connection.close()