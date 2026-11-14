
from datetime import timedelta


# 1. Complaint without customer
def generate_missing_customer(connection):
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE complaints
        SET customer_id = NULL
        WHERE complaint_id = (
            SELECT complaint_id
            FROM complaints
            WHERE customer_id IS NOT NULL
            ORDER BY complaint_id
            LIMIT 1
        )
        RETURNING complaint_id
    """)

    result = cursor.fetchone()
    if not result:
        print("No complaint available for anomaly 1")
        cursor.close()
        return

    complaint_id = result[0]

    cursor.execute("""
        INSERT INTO gt.ground_truth (
            ground_truth_id, entity_name, record_id,
            issue_type, expected_detection, scenario_name, notes
        )
        VALUES (
            'GT-ANOM-001', 'complaints', %s,
            'COMPLAINT_NO_CUSTOMER', TRUE,
            'Missing Customer',
            'Complaint has no customer reference'
        )
    """, (complaint_id,))

    connection.commit()
    cursor.close()
    print("Anomaly 1 created:", complaint_id)


# 2. Resolution before complaint creation
def generate_resolution_before_complaint(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT r.resolution_id, r.complaint_id
        FROM resolutions r
        JOIN complaints c ON c.complaint_id = r.complaint_id
        ORDER BY r.resolution_id
        LIMIT 1
    """)

    result = cursor.fetchone()
    if not result:
        print("No resolution available for anomaly 2")
        cursor.close()
        return

    resolution_id, complaint_id = result

    cursor.execute("""
        UPDATE resolutions
        SET resolved_at = (
            SELECT created_at - INTERVAL '1 day'
            FROM complaints
            WHERE complaint_id = %s
        )
        WHERE resolution_id = %s
    """, (complaint_id, resolution_id))

    cursor.execute("""
        INSERT INTO gt.ground_truth (
            ground_truth_id, entity_name, record_id,
            issue_type, expected_detection, scenario_name, notes
        )
        VALUES (
            'GT-ANOM-002', 'resolutions', %s,
            'RESOLUTION_BEFORE_COMPLAINT', TRUE,
            'Resolution Before Complaint',
            'Resolution timestamp is earlier than complaint creation'
        )
    """, (resolution_id,))

    connection.commit()
    cursor.close()
    print("Anomaly 2 created:", resolution_id)


# 3. Incorrect SLA pause
def generate_incorrect_sla_pause(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT sla_id, complaint_id, started_at
        FROM sla_clocks
        WHERE is_paused = FALSE
        LIMIT 1
    """)

    result = cursor.fetchone()
    if not result:
        print("No SLA clock available for anomaly 3")
        cursor.close()
        return

    sla_id, complaint_id, started_at = result
    pause_time = started_at + timedelta(minutes=30)

    cursor.execute("""
        UPDATE sla_clocks
        SET is_paused = TRUE,
            paused_at = %s
        WHERE sla_id = %s
    """, (pause_time, sla_id))

    cursor.execute("""
        INSERT INTO sla_events (
            sla_event_id, sla_id, event_type, event_time, reason
        )
        VALUES (%s, %s, 'PAUSED', %s, %s)
    """, (
        f"SLE-{complaint_id}-ANOM-003",
        sla_id,
        pause_time,
        "Invalid pause reason"
    ))

    cursor.execute("""
        INSERT INTO gt.ground_truth (
            ground_truth_id, entity_name, record_id,
            issue_type, expected_detection, scenario_name, notes
        )
        VALUES (
            'GT-ANOM-003', 'sla_clocks', %s,
            'SLA_PAUSE_INCORRECT', TRUE,
            'Incorrect SLA Pause',
            'SLA paused without a valid customer waiting reason'
        )
    """, (sla_id,))

    connection.commit()
    cursor.close()
    print("Anomaly 3 created:", complaint_id)


# 4. Repeat complaint not linked
def generate_repeat_not_linked(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            customer_id, order_id, product_id, category_id,
            priority_rule_id, complaint_text, channel, sentiment,
            severity, priority, priority_score, class_rule_fired,
            is_safety_related, created_at
        FROM complaints
        WHERE customer_id IS NOT NULL
        LIMIT 1
    """)

    row = cursor.fetchone()
    if not row:
        print("No complaint available for anomaly 4")
        cursor.close()
        return

    created_at = row[13] + timedelta(days=1)

    cursor.execute("""
        INSERT INTO complaints (
            complaint_id, customer_id, order_id, product_id,
            category_id, priority_rule_id, complaint_text,
            channel, sentiment, severity, priority,
            priority_score, class_rule_fired, is_safety_related,
            is_repeat, repeat_of_complaint_id, status,
            created_at, updated_at
        )
        VALUES (
            'CMP-2026-999999',
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s,
            TRUE, NULL, 'OPEN', %s, %s
        )
    """, tuple(row[:13]) + (created_at, created_at))

    cursor.execute("""
        INSERT INTO gt.ground_truth (
            ground_truth_id, entity_name, record_id,
            issue_type, expected_detection, scenario_name, notes
        )
        VALUES (
            'GT-ANOM-004', 'complaints', 'CMP-2026-999999',
            'REPEAT_NOT_LINKED', TRUE,
            'Repeat Not Linked',
            'Repeat complaint has no reference to original complaint'
        )
    """)

    connection.commit()
    cursor.close()
    print("Anomaly 4 created: CMP-2026-999999")


# 5. Safety complaint assigned to general support
def generate_safety_low_queue(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT complaint_id, created_at
        FROM complaints
        WHERE is_safety_related = TRUE
        LIMIT 1
    """)

    result = cursor.fetchone()
    if not result:
        print("No safety complaint available for anomaly 5")
        cursor.close()
        return

    complaint_id, created_at = result

    cursor.execute("""
        SELECT assignment_id, agent_id
        FROM complaint_assignments
        WHERE complaint_id = %s
          AND ended_at IS NULL
    """, (complaint_id,))

    assignment = cursor.fetchone()
    if not assignment:
        print("No current assignment found for:", complaint_id)
        cursor.close()
        return

    old_assignment, agent_id = assignment
    assigned_time = created_at + timedelta(hours=1)

    # End the existing assignment
    cursor.execute("""
        UPDATE complaint_assignments
        SET ended_at = %s
        WHERE assignment_id = %s
    """, (assigned_time, old_assignment))

    # Create a new assignment to the general support team
    cursor.execute("""
        INSERT INTO complaint_assignments (
            assignment_id, complaint_id, team_id, agent_id,
            assigned_at, assignment_reason
        )
        VALUES (%s, %s, 'TEAM-01', %s, %s, %s)
    """, (
        f"ASG-{complaint_id}-ANOM-005",
        complaint_id,
        agent_id,
        assigned_time,
        "Intentionally assigned to general support"
    ))

    cursor.execute("""
        INSERT INTO gt.ground_truth (
            ground_truth_id, entity_name, record_id,
            issue_type, expected_detection, scenario_name, notes
        )
        VALUES (
            'GT-ANOM-005', 'complaints', %s,
            'SAFETY_LOW_QUEUE', TRUE,
            'Safety Low Queue',
            'Safety complaint assigned to general support'
        )
    """, (complaint_id,))

    connection.commit()
    cursor.close()
    print("Anomaly 5 created:", complaint_id)


def generate_survey_before_closure(connection):
    cursor = connection.cursor()

    cursor.execute("""
        SELECT s.survey_id, s.complaint_id, c.created_at
        FROM surveys s
        JOIN complaints c
          ON c.complaint_id = s.complaint_id
        WHERE c.status = 'RESOLVED'
        ORDER BY s.survey_id
        LIMIT 1
    """)

    result = cursor.fetchone()

    if not result:
        print("No suitable survey found for anomaly 6")
        cursor.close()
        return

    survey_id, complaint_id, created_at = result

    cursor.execute("""
        UPDATE surveys
        SET sent_at = %s,
            submitted_at = NULL
        WHERE survey_id = %s
    """, (created_at - timedelta(days=1), survey_id))

    cursor.execute("""
        INSERT INTO gt.ground_truth (
            ground_truth_id, entity_name, record_id,
            issue_type, expected_detection, scenario_name, notes
        )
        VALUES (
            'GT-ANOM-006', 'surveys', %s,
            'SURVEY_BEFORE_CLOSURE', TRUE,
            'Survey Before Closure',
            'Survey sent before complaint resolution'
        )
    """, (survey_id,))

    connection.commit()
    cursor.close()

    print("Anomaly 6 created:", survey_id)
