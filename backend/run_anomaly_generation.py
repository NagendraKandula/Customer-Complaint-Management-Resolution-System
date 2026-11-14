from data_generation.db_connection import get_connection

from data_generation.generators.anomaly_generator import (
    generate_missing_customer,
    generate_resolution_before_complaint,
    generate_incorrect_sla_pause,
    generate_repeat_not_linked,
    generate_safety_low_queue
)

connection = get_connection()

try:
    print("Starting anomaly generation...")

    generate_missing_customer(connection)
    generate_resolution_before_complaint(connection)
    generate_incorrect_sla_pause(connection)
    generate_repeat_not_linked(connection)
    generate_safety_low_queue(connection)

    print("Anomaly generation completed!")

finally:
    connection.close()