
from datetime import timedelta

from data_generation.config import (
    DATASET_SIZE,
    SCALE,
)

from data_generation.random_utils import (
    random_integer,
    random_weighted_choice,
)

from data_generation.id_generator import id_generator

from data_generation.generators.order_generator import insert_records


# ============================================================
# 1. FINAL STATUS DISTRIBUTION
# ============================================================

FINAL_STATUS_DISTRIBUTION = {
    "IN_PROGRESS": 0.25,
    "WAITING_FOR_CUSTOMER": 0.15,
    "ESCALATED": 0.10,
    "RESOLVED": 0.20,
    "CLOSED": 0.20,
    "REOPENED": 0.10,
}


# ============================================================
# 2. LOAD ASSIGNMENT REFERENCE DATA
# ============================================================

def load_status_history_reference_data(connection):
    """
    Load complaints and their current active assignments.
    """

    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                c.complaint_id,
                c.updated_at,
                c.status,
                ca.agent_id,
                ca.assigned_at
            FROM complaints c
            JOIN complaint_assignments ca
                ON c.complaint_id = ca.complaint_id
            WHERE ca.ended_at IS NULL
            ORDER BY c.complaint_id
        """)

        complaints = []

        for row in cursor.fetchall():

            complaints.append({

                "complaint_id": row[0],
                "updated_at": row[1],
                "current_status": row[2],
                "agent_id": row[3],
                "assigned_at": row[4],

            })

        if not complaints:
            raise ValueError(
                "No active assignments found. "
                "Run assignment generation first."
            )

        return complaints

    finally:
        cursor.close()


# ============================================================
# 3. CREATE ONE STATUS HISTORY EVENT
# ============================================================

def add_status_event(
    history_records,
    complaint_id,
    old_status,
    new_status,
    changed_by,
    reason,
    changed_at,
):
    """
    Create a single complaint status history record.
    """

    history_id = id_generator.history_id(
        complaint_id
    )

    record = (
        history_id,
        complaint_id,
        old_status,
        new_status,
        changed_by,
        reason,
        changed_at,
    )

    history_records.append(record)


# ============================================================
# 4. GENERATE STATUS LIFECYCLE
# ============================================================

def generate_complaint_lifecycle(complaint):
    """
    Generate a chronological status journey
    for one complaint.

    Returns:
        history_records: list of status history tuples
        final_update: final complaint status information
    """

    complaint_id = complaint["complaint_id"]
    agent_id = complaint["agent_id"]

    assigned_at = complaint["assigned_at"]

    # Use the later timestamp as the starting point
    # for the next workflow transition.
    current_time = max(
        assigned_at,
        complaint["updated_at"],
    )

    history_records = []

    # --------------------------------------------------------
    # EVENT 1: CLASSIFIED -> ASSIGNED
    # --------------------------------------------------------

    add_status_event(
        history_records=history_records,
        complaint_id=complaint_id,
        old_status=None,
        new_status="ASSIGNED",
        changed_by="SYSTEM",
        reason="COMPLAINT_ASSIGNED_TO_AGENT",
        changed_at=assigned_at,
    )

    # --------------------------------------------------------
    # EVENT 2: ASSIGNED -> IN_PROGRESS
    # --------------------------------------------------------

    current_time += timedelta(
        minutes=random_integer(15, 180)
    )

    add_status_event(
        history_records=history_records,
        complaint_id=complaint_id,
        old_status="ASSIGNED",
        new_status="IN_PROGRESS",
        changed_by=agent_id,
        reason="AGENT_STARTED_WORKING",
        changed_at=current_time,
    )

    # --------------------------------------------------------
    # SELECT FINAL STATUS
    # --------------------------------------------------------

    final_status = random_weighted_choice(
        FINAL_STATUS_DISTRIBUTION
    )

    closed_at = None
    reopen_count = 0

    # --------------------------------------------------------
    # PATH 1: IN_PROGRESS
    # --------------------------------------------------------

    if final_status == "IN_PROGRESS":

        pass

    # --------------------------------------------------------
    # PATH 2: WAITING_FOR_CUSTOMER
    # --------------------------------------------------------

    elif final_status == "WAITING_FOR_CUSTOMER":

        current_time += timedelta(
            minutes=random_integer(30, 240)
        )

        add_status_event(
            history_records,
            complaint_id,
            "IN_PROGRESS",
            "WAITING_FOR_CUSTOMER",
            agent_id,
            "ADDITIONAL_CUSTOMER_INFORMATION_REQUIRED",
            current_time,
        )

    # --------------------------------------------------------
    # PATH 3: ESCALATED
    # --------------------------------------------------------

    elif final_status == "ESCALATED":

        current_time += timedelta(
            minutes=random_integer(30, 240)
        )

        add_status_event(
            history_records,
            complaint_id,
            "IN_PROGRESS",
            "ESCALATED",
            "SYSTEM",
            "COMPLAINT_ESCALATED_FOR_FURTHER_REVIEW",
            current_time,
        )

    # --------------------------------------------------------
    # PATH 4: RESOLVED
    # --------------------------------------------------------

    elif final_status == "RESOLVED":

        current_time += timedelta(
            hours=random_integer(1, 24)
        )

        add_status_event(
            history_records,
            complaint_id,
            "IN_PROGRESS",
            "RESOLVED",
            agent_id,
            "COMPLAINT_RESOLVED_BY_AGENT",
            current_time,
        )

    # --------------------------------------------------------
    # PATH 5: CLOSED
    # --------------------------------------------------------

    elif final_status == "CLOSED":

        # First resolve the complaint.
        current_time += timedelta(
            hours=random_integer(1, 24)
        )

        add_status_event(
            history_records,
            complaint_id,
            "IN_PROGRESS",
            "RESOLVED",
            agent_id,
            "COMPLAINT_RESOLVED_BY_AGENT",
            current_time,
        )

        # Then close it.
        current_time += timedelta(
            minutes=random_integer(30, 240)
        )

        closed_at = current_time

        add_status_event(
            history_records,
            complaint_id,
            "RESOLVED",
            "CLOSED",
            "SYSTEM",
            "COMPLAINT_CLOSED_AFTER_RESOLUTION",
            current_time,
        )

    # --------------------------------------------------------
    # PATH 6: REOPENED
    # --------------------------------------------------------

    elif final_status == "REOPENED":

        # Resolve the complaint first.
        current_time += timedelta(
            hours=random_integer(1, 24)
        )

        add_status_event(
            history_records,
            complaint_id,
            "IN_PROGRESS",
            "RESOLVED",
            agent_id,
            "COMPLAINT_RESOLVED_BY_AGENT",
            current_time,
        )

        # Close the complaint.
        current_time += timedelta(
            minutes=random_integer(30, 240)
        )

        closed_at = current_time

        add_status_event(
            history_records,
            complaint_id,
            "RESOLVED",
            "CLOSED",
            "SYSTEM",
            "COMPLAINT_CLOSED_AFTER_RESOLUTION",
            current_time,
        )

        # Customer reports that the problem still exists.
        current_time += timedelta(
            hours=random_integer(24, 72)
        )

        add_status_event(
            history_records,
            complaint_id,
            "CLOSED",
            "REOPENED",
            "SYSTEM",
            "CUSTOMER_REPORTED_ISSUE_NOT_RESOLVED",
            current_time,
        )

        reopen_count = 1

    # --------------------------------------------------------
    # FINAL COMPLAINT UPDATE
    # --------------------------------------------------------

    final_update = {
        "complaint_id": complaint_id,
        "final_status": final_status,
        "updated_at": current_time,
        "closed_at": closed_at,
        "reopen_count": reopen_count,
    }

    return history_records, final_update


# ============================================================
# 5. GENERATE ALL COMPLAINT STATUS HISTORIES
# ============================================================

def generate_status_history_records(complaints):

    all_history_records = []
    final_updates = []

    status_counts = {
        status: 0
        for status in FINAL_STATUS_DISTRIBUTION
    }

    for complaint in complaints:

        history_records, final_update = (
            generate_complaint_lifecycle(complaint)
        )

        all_history_records.extend(
            history_records
        )

        final_updates.append(
            final_update
        )

        status_counts[
            final_update["final_status"]
        ] += 1

    return (
        all_history_records,
        final_updates,
        status_counts,
    )


# ============================================================
# 6. BULK UPDATE FINAL COMPLAINT STATUSES
# ============================================================

def bulk_update_final_complaint_status(
    cursor,
    final_updates,
    batch_size=500,
):
    """
    Update final status, updated_at, closed_at
    and reopen_count using bulk SQL.
    """

    for start in range(
        0,
        len(final_updates),
        batch_size,
    ):

        batch = final_updates[
            start:start + batch_size
        ]

        values_sql = ", ".join(
            ["(%s::TEXT, %s::TEXT, %s::TIMESTAMPTZ, "
             "%s::TIMESTAMPTZ, %s::INTEGER)"]
            * len(batch)
        )

        parameters = []

        for item in batch:

            parameters.extend([
                item["complaint_id"],
                item["final_status"],
                item["updated_at"],
                item["closed_at"],
                item["reopen_count"],
            ])

        query = f"""
            UPDATE complaints AS c
            SET
                status = v.final_status,
                updated_at = GREATEST(
                    c.updated_at,
                    v.updated_at
                ),
                closed_at = v.closed_at,
                reopen_count = v.reopen_count
            FROM (
                VALUES {values_sql}
            ) AS v(
                complaint_id,
                final_status,
                updated_at,
                closed_at,
                reopen_count
            )
            WHERE c.complaint_id = v.complaint_id
        """

        cursor.execute(
            query,
            parameters
        )

        print(
            "Updated complaint final statuses:",
            min(
                start + batch_size,
                len(final_updates)
            ),
            "/",
            len(final_updates),
            flush=True,
        )


# ============================================================
# 7. MAIN STATUS HISTORY GENERATION
# ============================================================

def run_status_history_generation(connection):

    print(
        "Loading assigned complaints...",
        flush=True
    )

    complaints = load_status_history_reference_data(
        connection
    )

    expected_complaints = round(
        DATASET_SIZE["complaints"] * SCALE
    )

    print(
        "Assigned complaints available:",
        len(complaints),
        flush=True
    )

    if len(complaints) != expected_complaints:

        raise ValueError(
            f"Expected {expected_complaints} assignments, "
            f"found {len(complaints)}."
        )

    # Validate that all complaints are currently assigned.
    invalid_statuses = [
        complaint
        for complaint in complaints
        if complaint["current_status"] != "ASSIGNED"
    ]

    if invalid_statuses:

        raise ValueError(
            f"{len(invalid_statuses)} complaints "
            "are not in ASSIGNED status."
        )

    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # A. PREVENT DUPLICATE HISTORY
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM complaint_status_history
        """)

        existing_history = cursor.fetchone()[0]

        if existing_history > 0:

            raise RuntimeError(
                "Status history already exists. "
                "Refusing duplicate generation."
            )

        # ----------------------------------------------------
        # B. GENERATE STATUS HISTORY
        # ----------------------------------------------------

        print(
            "\nGenerating complaint lifecycles...",
            flush=True
        )

        (
            history_records,
            final_updates,
            status_counts,
        ) = generate_status_history_records(
            complaints
        )

        print(
            "Generated history events:",
            len(history_records),
            flush=True
        )

        # ----------------------------------------------------
        # C. INSERT STATUS HISTORY
        # ----------------------------------------------------

        print(
            "\nInserting status history...",
            flush=True
        )

        insert_records(
            connection,
            "complaint_status_history",
            [
                "history_id",
                "complaint_id",
                "old_status",
                "new_status",
                "changed_by",
                "reason",
                "changed_at",
            ],
            history_records,
        )

        # ----------------------------------------------------
        # D. UPDATE CURRENT COMPLAINT STATUS
        # ----------------------------------------------------

        print(
            "\nUpdating final complaint statuses...",
            flush=True
        )

        bulk_update_final_complaint_status(
            cursor,
            final_updates,
        )

        # ----------------------------------------------------
        # E. COMMIT
        # ----------------------------------------------------

        print(
            "\nCommitting transaction...",
            flush=True
        )

        connection.commit()

        print(
            "\nStatus history generation completed!",
            flush=True
        )

        print(
            "Total complaints:",
            len(complaints)
        )

        print(
            "Total history events:",
            len(history_records)
        )

        print(
            "\nFinal complaint status distribution:"
        )

        for status, count in status_counts.items():

            print(
                status,
                ":",
                count
            )

    except Exception:

        connection.rollback()

        print(
            "Status history generation failed. "
            "Transaction rolled back.",
            flush=True
        )

        raise

    finally:

        cursor.close()
