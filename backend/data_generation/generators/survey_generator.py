
from datetime import timedelta

from data_generation.id_generator import id_generator
from data_generation.random_utils import random_choice, random_boolean, random_integer
from data_generation.generators.order_generator import insert_records


FEEDBACK = {
    1: ["Very poor experience", "Not satisfied with the resolution"],
    2: ["Needs improvement", "Issue was not handled properly"],
    3: ["Average experience", "Issue was partially addressed"],
    4: ["Good support experience", "Satisfied with the response"],
    5: ["Excellent support", "Very happy with the resolution"]
}


def run_survey_generation(connection):
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM surveys")
        if cursor.fetchone()[0] > 0:
            raise ValueError("Surveys already exist")

        cursor.execute("""
            SELECT r.complaint_id, r.resolution_id,
                   COALESCE(c.closed_at, r.resolved_at)
            FROM resolutions r
            JOIN complaints c ON c.complaint_id = r.complaint_id
            WHERE r.is_final = TRUE
        """)

        rows = cursor.fetchall()
        records = []

        for complaint_id, resolution_id, base_time in rows:
            sent_at = base_time + timedelta(
                minutes=random_integer(15, 1440)
            )

            submitted = random_boolean(0.70)
            submitted_at = None
            rating = None
            feedback = None

            if submitted:
                submitted_at = sent_at + timedelta(
                    minutes=random_integer(5, 1440)
                )
                rating = random_integer(1, 5)
                feedback = random_choice(FEEDBACK[rating])

            records.append((
                id_generator.survey_id(complaint_id),
                complaint_id,
                resolution_id,
                sent_at,
                submitted_at,
                rating,
                feedback
            ))

        insert_records(
            connection, "surveys",
            ["survey_id", "complaint_id", "resolution_id",
             "sent_at", "submitted_at", "rating", "feedback"],
            records
        )

        connection.commit()
        print("Surveys inserted:", len(records))

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
