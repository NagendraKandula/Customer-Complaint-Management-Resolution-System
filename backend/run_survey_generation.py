from data_generation.db_connection import get_connection
from data_generation.generators.survey_generator import run_survey_generation

connection = get_connection()
try:
    run_survey_generation(connection)
finally:
    connection.close()