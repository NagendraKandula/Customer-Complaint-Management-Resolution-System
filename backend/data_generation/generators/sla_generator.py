
from datetime import datetime, timezone, timedelta

from data_generation.id_generator import id_generator
from data_generation.generators.order_generator import insert_records


def run_sla_generation(connection):
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM sla_clocks")
        if cursor.fetchone()[0] > 0:
            raise ValueError("SLA clocks already exist")

        cursor.execute("SELECT COUNT(*) FROM sla_events")
        if cursor.fetchone()[0] > 0:
            raise ValueError("SLA events already exist")

        cursor.execute("""
            SELECT c.complaint_id, c.priority, c.status, c.created_at,
                   p.response_minutes, p.resolution_minutes,
                   (SELECT MIN(m.sent_at)
                    FROM complaint_messages m
                    WHERE m.complaint_id = c.complaint_id
                    AND m.sender_type = 'AGENT'),
                   (SELECT MIN(h.changed_at)
                    FROM complaint_status_history h
                    WHERE h.complaint_id = c.complaint_id
                    AND h.new_status = 'RESOLVED')
            FROM complaints c
            JOIN sla_policy p ON p.priority_level = c.priority
            ORDER BY c.complaint_id
        """)

        complaints = cursor.fetchall()
        now = datetime.now(timezone.utc)

        clocks = []
        events = []
        event_no = 1

        for i, row in enumerate(complaints, 1):
            (complaint_id, priority, status, started,
             response_min, resolution_min, first_response,
             resolved_at) = row

            response_deadline = started + timedelta(minutes=response_min)
            resolution_deadline = started + timedelta(minutes=resolution_min)

            response_check = first_response or now
            resolution_check = resolved_at or now

            response_breached = response_check > response_deadline
            resolution_breached = resolution_check > resolution_deadline

            sla_id = id_generator.sla_id(complaint_id)

            clocks.append((
                sla_id, complaint_id, priority, started,
                response_deadline, resolution_deadline,
                first_response, resolved_at,
                response_breached, resolution_breached,
                False, None, 0
            ))

            def add_event(event_type, event_time, reason):
                nonlocal event_no
                events.append((
                    f"SLE-{event_no:07d}", sla_id,
                    event_type, event_time, reason
                ))
                event_no += 1

            add_event("STARTED", started, "SLA clock started")

            if first_response:
                add_event(
                    "FIRST_RESPONSE", first_response,
                    "First agent response"
                )

            if response_breached:
                add_event(
                    "RESPONSE_BREACHED", response_deadline,
                    "Response deadline exceeded"
                )

            if resolution_breached:
                add_event(
                    "RESOLUTION_BREACHED", resolution_deadline,
                    "Resolution deadline exceeded"
                )

            if resolved_at:
                add_event(
                    "COMPLETED", resolved_at,
                    "Complaint resolution recorded"
                )

            if status == "ESCALATED":
                add_event(
                    "ESCALATED", now,
                    "Complaint escalated"
                )

        insert_records(
            connection, "sla_clocks",
            ["sla_id", "complaint_id", "priority_level",
             "started_at", "response_deadline", "resolution_deadline",
             "first_response_at", "resolved_at",
             "response_breached", "resolution_breached",
             "is_paused", "paused_at", "total_paused_minutes"],
            clocks
        )

        insert_records(
            connection, "sla_events",
            ["sla_event_id", "sla_id", "event_type",
             "event_time", "reason"],
            events
        )

        connection.commit()
        print("SLA clocks inserted:", len(clocks))
        print("SLA events inserted:", len(events))

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
