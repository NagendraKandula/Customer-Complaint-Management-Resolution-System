from data_generation.db_connection import get_connection
from data_generation.generators.anomaly_generator import (
    generate_survey_before_closure
)

connection = get_connection()

try:
    generate_survey_before_closure(connection)
finally:
    connection.close()