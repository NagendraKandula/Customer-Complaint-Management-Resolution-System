from data_generation.db_connection import get_connection
from data_generation.generators.anomaly_generator import (
    generate_repeat_not_linked,
    generate_safety_low_queue
)

connection = get_connection()

try:
    generate_repeat_not_linked(connection)
    generate_safety_low_queue(connection)
finally:
    connection.close()