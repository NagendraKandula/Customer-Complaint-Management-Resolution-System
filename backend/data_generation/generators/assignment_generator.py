
from datetime import timedelta

from data_generation.config import (
    DATASET_SIZE,
    SCALE,
)

from data_generation.random_utils import random_integer

from data_generation.id_generator import id_generator

from data_generation.generators.order_generator import insert_records


# ============================================================
# 1. BULK UPDATE COMPLAINT STATUS
# ============================================================


def bulk_update_complaint_status(cursor, assignments, batch_size=500):
    """
    Bulk update complaint statuses.

    Explicitly cast assigned_at to TIMESTAMPTZ
    to avoid PostgreSQL type inference issues.
    """

    for start in range(0, len(assignments), batch_size):

        batch = assignments[start:start + batch_size]

        # Explicitly define the parameter types.
        values_sql = ", ".join(
            ["(%s::TIMESTAMPTZ, %s::TEXT)"] * len(batch)
        )

        parameters = []

        for item in batch:
            parameters.extend([
                item["assigned_at"],
                item["complaint_id"],
            ])

        query = f"""
            UPDATE complaints AS c
            SET
                status = 'ASSIGNED',
                updated_at = GREATEST(
                    c.updated_at,
                    v.assigned_at
                )
            FROM (VALUES {values_sql})
                AS v(assigned_at, complaint_id)
            WHERE c.complaint_id = v.complaint_id
        """

        cursor.execute(query, parameters)

        print(
            f"Updated complaint statuses: "
            f"{min(start + batch_size, len(assignments))}"
            f"/{len(assignments)}",
            flush=True
        )

# ============================================================
# 2. BULK UPDATE AGENT MESSAGES
# ============================================================

def bulk_update_agent_messages(cursor, assignments, batch_size=500):
    """
    Update agent message sender IDs using bulk SQL.

    Each AGENT message will reference the agent assigned
    to its corresponding complaint.
    """

    for start in range(0, len(assignments), batch_size):

        batch = assignments[start:start + batch_size]

        values_sql = ", ".join(
            ["(%s, %s)"] * len(batch)
        )

        parameters = []

        for item in batch:
            parameters.extend([
                item["agent_id"],
                item["complaint_id"],
            ])

        query = f"""
            UPDATE complaint_messages AS m
            SET
                sender_id = v.agent_id
            FROM (VALUES {values_sql})
                AS v(agent_id, complaint_id)
            WHERE m.complaint_id = v.complaint_id
              AND m.sender_type = 'AGENT'
        """

        cursor.execute(query, parameters)

        print(
            f"Updated agent messages: "
            f"{min(start + batch_size, len(assignments))}"
            f"/{len(assignments)}",
            flush=True
        )


# ============================================================
# 3. LOAD COMPLAINTS AND ACTIVE AGENTS
# ============================================================

def load_assignment_reference_data(connection):
    """
    Load complaints, their default teams and active agents.
    """

    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                c.complaint_id,
                c.priority,
                c.is_safety_related,
                c.is_repeat,
                c.created_at,
                cc.default_team_id,
                cc.category_name
            FROM complaints c
            JOIN complaint_categories cc
                ON c.category_id = cc.category_id
            ORDER BY c.complaint_id
        """)

        complaints = [
            {
                "complaint_id": row[0],
                "priority": row[1],
                "is_safety_related": row[2],
                "is_repeat": row[3],
                "created_at": row[4],
                "team_id": row[5],
                "category_name": row[6],
            }
            for row in cursor.fetchall()
        ]

        cursor.execute("""
            SELECT
                agent_id,
                team_id
            FROM agents
            WHERE is_active = TRUE
            ORDER BY agent_id
        """)

        agents = {}

        for agent_id, team_id in cursor.fetchall():

            agents.setdefault(
                team_id, []
            ).append(agent_id)

        if not complaints:
            raise ValueError(
                "No complaints found. Generate complaints first."
            )

        if not agents:
            raise ValueError(
                "No active agents found."
            )

        return complaints, agents

    finally:
        cursor.close()


# ============================================================
# 4. DETERMINE ASSIGNMENT REASON
# ============================================================

def get_assignment_reason(complaint):
    """
    Explain why a complaint is assigned to a team.
    """

    if complaint["is_safety_related"]:
        return "PRODUCT_SAFETY_SPECIALIST"

    if complaint["priority"] == "P1":
        return "HIGH_PRIORITY_ROUTING"

    if complaint["is_repeat"]:
        return "REPEAT_COMPLAINT_FOLLOWUP"

    return "CATEGORY_DEFAULT_TEAM"


# ============================================================
# 5. GENERATE ASSIGNMENT RECORDS
# ============================================================

def generate_assignment_records(complaints, agents_by_team):
    """
    Generate one assignment for every complaint.

    Selects the least-loaded active agent within
    the complaint category's default team.
    """

    assignments = []

    # Track the number of assignments per agent.
    agent_workload = {
        agent_id: 0
        for team_agents in agents_by_team.values()
        for agent_id in team_agents
    }

    for complaint in complaints:

        complaint_id = complaint["complaint_id"]
        team_id = complaint["team_id"]

        # Find agents belonging to the required team.
        team_agents = agents_by_team.get(team_id, [])

        if not team_agents:
            raise ValueError(
                f"No active agents available for team {team_id}"
            )

        # Select the agent with the lowest assignment count.
        agent_id = min(
            team_agents,
            key=lambda agent: (
                agent_workload[agent],
                agent
            )
        )

        agent_workload[agent_id] += 1

        # Assignment happens shortly after complaint creation.
        assigned_at = complaint["created_at"] + timedelta(
            minutes=random_integer(1, 60)
        )

        assignment_id = id_generator.assignment_id(
            complaint_id
        )

        assignment_reason = get_assignment_reason(
            complaint
        )

        assignments.append({

            "record": (
                assignment_id,
                complaint_id,
                team_id,
                agent_id,
                assigned_at,
                None,
                assignment_reason,
            ),

            "complaint_id": complaint_id,
            "agent_id": agent_id,
            "assigned_at": assigned_at,

        })

    return assignments


# ============================================================
# 6. MAIN ASSIGNMENT GENERATION
# ============================================================

def run_assignment_generation(connection):

    print(
        "Loading complaints and agents...",
        flush=True
    )

    complaints, agents_by_team = load_assignment_reference_data(
        connection
    )

    print(
        "Complaints available:",
        len(complaints),
        flush=True
    )

    print(
        "Teams with active agents:",
        len(agents_by_team),
        flush=True
    )

    # Validate expected complaint count.
    expected_complaints = round(
        DATASET_SIZE["complaints"] * SCALE
    )

    if len(complaints) != expected_complaints:

        raise ValueError(
            f"Expected {expected_complaints} complaints, "
            f"found {len(complaints)}."
        )

    print(
        "\nGenerating assignment records...",
        flush=True
    )

    assignments = generate_assignment_records(
        complaints,
        agents_by_team
    )

    print(
        "Generated assignments:",
        len(assignments),
        flush=True
    )

    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # A. PREVENT DUPLICATE ASSIGNMENTS
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM complaint_assignments
        """)

        existing_assignments = cursor.fetchone()[0]

        if existing_assignments > 0:

            raise RuntimeError(
                "Assignments already exist. "
                "Refusing duplicate insertion."
            )

        # ----------------------------------------------------
        # B. VALIDATE AGENT MESSAGES
        # ----------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM complaints c
            WHERE (
                SELECT COUNT(*)
                FROM complaint_messages m
                WHERE m.complaint_id = c.complaint_id
                  AND m.sender_type = 'AGENT'
            ) <> 1
        """)

        invalid_agent_messages = cursor.fetchone()[0]

        if invalid_agent_messages > 0:

            raise ValueError(
                f"{invalid_agent_messages} complaints do not "
                "have exactly one agent message."
            )

        # ----------------------------------------------------
        # C. INSERT ASSIGNMENT RECORDS
        # ----------------------------------------------------

        print(
            "\nInserting assignment records...",
            flush=True
        )

        insert_records(
            connection,
            "complaint_assignments",
            [
                "assignment_id",
                "complaint_id",
                "team_id",
                "agent_id",
                "assigned_at",
                "ended_at",
                "assignment_reason",
            ],
            [
                item["record"]
                for item in assignments
            ]
        )

        # ----------------------------------------------------
        # D. BULK UPDATE COMPLAINT STATUS
        # ----------------------------------------------------

        print(
            "\nUpdating complaint statuses...",
            flush=True
        )

        bulk_update_complaint_status(
            cursor,
            assignments
        )

        # ----------------------------------------------------
        # E. BULK UPDATE AGENT MESSAGE SENDER IDs
        # ----------------------------------------------------

        print(
            "\nUpdating agent messages...",
            flush=True
        )

        bulk_update_agent_messages(
            cursor,
            assignments
        )

        # ----------------------------------------------------
        # F. COMMIT TRANSACTION
        # ----------------------------------------------------

        print(
            "\nCommitting transaction...",
            flush=True
        )

        connection.commit()

        print(
            "\nAssignment generation completed!",
            flush=True
        )

        print(
            "Total assignments:",
            len(assignments),
            flush=True
        )

        # ----------------------------------------------------
        # G. DISPLAY AGENT WORKLOAD
        # ----------------------------------------------------

        print(
            "\nAgent assignment distribution:",
            flush=True
        )

        workload = {}

        for item in assignments:

            agent_id = item["agent_id"]

            workload[agent_id] = (
                workload.get(agent_id, 0) + 1
            )

        for agent_id in sorted(workload):

            print(
                agent_id,
                ":",
                workload[agent_id],
                flush=True
            )

    except Exception:

        connection.rollback()

        print(
            "Assignment generation failed. "
            "Transaction rolled back.",
            flush=True
        )

        raise

    finally:

        cursor.close()
