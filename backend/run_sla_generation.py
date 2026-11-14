from data_generation.db_connection import get_connection
from data_generation.generators.sla_generator import run_sla_generation

connection = get_connection()
try:
    run_sla_generation(connection)
finally:
    connection.close()