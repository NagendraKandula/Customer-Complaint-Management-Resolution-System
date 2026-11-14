
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data_generation.db_connection import get_connection


# --------------------------------------------------
# 1. APPLICATION CONFIGURATION
# --------------------------------------------------

app = FastAPI(
    title="Customer Complaint Resolution API",
    description="REST APIs for complaint management and analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# 2. DATABASE HELPER FUNCTIONS
# --------------------------------------------------

def fetch_all(query, params=()):
    """Execute SELECT query and return all rows as dictionaries."""

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(query, params)

        columns = [column[0] for column in cursor.description]
        rows = cursor.fetchall()

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    finally:
        connection.close()


def fetch_one(query, params=()):
    """Execute SELECT query and return one row as a dictionary."""

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(query, params)

        row = cursor.fetchone()

        if row is None:
            return None

        columns = [column[0] for column in cursor.description]

        return dict(zip(columns, row))

    finally:
        connection.close()


# --------------------------------------------------
# 3. HEALTH CHECK
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Complaint Resolution API is running",
        "status": "healthy"
    }


@app.get("/api/health")
def health_check():
    try:
        result = fetch_one("SELECT 1 AS database_connected")

        return {
            "api": "healthy",
            "database": "connected",
            "result": result
        }

    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(error)}"
        )


# --------------------------------------------------
# 4. DASHBOARD SUMMARY
# --------------------------------------------------

@app.get("/api/dashboard/summary")
def dashboard_summary():

    result = fetch_one("""
        SELECT
            COUNT(*) AS total_complaints,

            COUNT(*) FILTER (
                WHERE status NOT IN ('RESOLVED', 'CLOSED')
            ) AS open_complaints,

            COUNT(*) FILTER (
                WHERE status = 'RESOLVED'
            ) AS resolved_complaints,

            COUNT(*) FILTER (
                WHERE status = 'CLOSED'
            ) AS closed_complaints,

            COUNT(*) FILTER (
                WHERE status = 'REOPENED'
            ) AS reopened_complaints

        FROM complaints
    """)

    return result


# --------------------------------------------------
# 5. COMPLAINT STATUS DISTRIBUTION
# --------------------------------------------------

@app.get("/api/dashboard/status")
def dashboard_status():

    return fetch_all("""
        SELECT
            status,
            COUNT(*) AS complaint_count

        FROM complaints

        GROUP BY status

        ORDER BY complaint_count DESC
    """)


# --------------------------------------------------
# 6. PRIORITY DISTRIBUTION
# --------------------------------------------------

@app.get("/api/dashboard/priority")
def dashboard_priority():

    return fetch_all("""
        SELECT
            priority,
            COUNT(*) AS complaint_count

        FROM complaints

        GROUP BY priority

        ORDER BY priority
    """)


# --------------------------------------------------
# 7. SEVERITY DISTRIBUTION
# --------------------------------------------------

@app.get("/api/dashboard/severity")
def dashboard_severity():

    return fetch_all("""
        SELECT
            severity,
            COUNT(*) AS complaint_count

        FROM complaints

        GROUP BY severity

        ORDER BY severity
    """)


# --------------------------------------------------
# 8. SLA COMPLIANCE
# --------------------------------------------------

@app.get("/api/dashboard/sla")
def dashboard_sla():

    return fetch_one("""
        SELECT
            COUNT(*) AS total_sla_records,

            COUNT(*) FILTER (
                WHERE response_breached = TRUE
            ) AS response_breached,

            COUNT(*) FILTER (
                WHERE resolution_breached = TRUE
            ) AS resolution_breached,

            COUNT(*) FILTER (
                WHERE response_breached = FALSE
                  AND resolution_breached = FALSE
            ) AS fully_compliant,

            COUNT(*) FILTER (
                WHERE is_paused = TRUE
            ) AS currently_paused

        FROM sla_clocks
    """)


# --------------------------------------------------
# 9. CATEGORY ANALYTICS
# --------------------------------------------------

@app.get("/api/analytics/categories")
def category_analytics():

    # The categories table was not found in public.
    # Therefore, return category_id counts directly.

    return fetch_all("""
        SELECT
            COALESCE(category_id, 'UNCATEGORIZED') AS category_id,
            COUNT(*) AS complaint_count

        FROM complaints

        GROUP BY category_id

        ORDER BY complaint_count DESC
    """)


# --------------------------------------------------
# 10. AGENT PERFORMANCE
# --------------------------------------------------

@app.get("/api/analytics/agents")
def agent_analytics():

    return fetch_all("""
        SELECT
            a.agent_id,
            a.agent_name,
            t.team_name,

            COUNT(ca.assignment_id) AS total_assignments,

            COUNT(ca.assignment_id) FILTER (
                WHERE ca.ended_at IS NULL
            ) AS current_assignments

        FROM agents a

        LEFT JOIN teams t
            ON a.team_id = t.team_id

        LEFT JOIN complaint_assignments ca
            ON a.agent_id = ca.agent_id

        GROUP BY
            a.agent_id,
            a.agent_name,
            t.team_name

        ORDER BY current_assignments DESC

        LIMIT 10
    """)


# --------------------------------------------------
# 11. COMPLAINT LIST WITH FILTERS AND PAGINATION
# --------------------------------------------------

@app.get("/api/complaints")
def get_complaints(
    status: str = None,
    priority: str = None,
    severity: str = None,
    channel: str = None,
    search: str = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):

    conditions = []
    params = []

    if status:
        conditions.append("status = %s")
        params.append(status.upper())

    if priority:
        conditions.append("priority = %s")
        params.append(priority.upper())

    if severity:
        conditions.append("severity = %s")
        params.append(severity.upper())

    if channel:
        conditions.append("channel = %s")
        params.append(channel.upper())

    if search:
        conditions.append(
            "(complaint_id ILIKE %s OR complaint_text ILIKE %s)"
        )
        params.extend([f"%{search}%", f"%{search}%"])

    where_clause = ""

    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    count_query = f"""
        SELECT COUNT(*) AS total
        FROM complaints
        {where_clause}
    """

    count_result = fetch_one(count_query, tuple(params))

    data_query = f"""
        SELECT
            complaint_id,
            customer_id,
            order_id,
            product_id,
            category_id,
            complaint_text,
            channel,
            sentiment,
            severity,
            priority,
            priority_score,
            is_safety_related,
            is_repeat,
            status,
            reopen_count,
            created_at,
            updated_at

        FROM complaints

        {where_clause}

        ORDER BY created_at DESC

        LIMIT %s OFFSET %s
    """

    data_params = tuple(params) + (limit, offset)

    complaints = fetch_all(data_query, data_params)

    return {
        "total": count_result["total"],
        "limit": limit,
        "offset": offset,
        "complaints": complaints
    }


# --------------------------------------------------
# 12. COMPLAINT DETAILS
# --------------------------------------------------

@app.get("/api/complaints/{complaint_id}")
def get_complaint_details(complaint_id: str):

    complaint = fetch_one("""
        SELECT
            c.*,
            cu.full_name AS customer_name,
            cu.email AS customer_email,
            cu.phone AS customer_phone

        FROM complaints c

        LEFT JOIN customers cu
            ON c.customer_id = cu.customer_id

        WHERE c.complaint_id = %s
    """, (complaint_id,))

    if not complaint:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    history = fetch_all("""
        SELECT *
        FROM complaint_status_history

        WHERE complaint_id = %s

        ORDER BY changed_at
    """, (complaint_id,))

    assignments = fetch_all("""
        SELECT
            ca.*,
            a.agent_name,
            t.team_name

        FROM complaint_assignments ca

        LEFT JOIN agents a
            ON ca.agent_id = a.agent_id

        LEFT JOIN teams t
            ON ca.team_id = t.team_id

        WHERE ca.complaint_id = %s

        ORDER BY ca.assigned_at
    """, (complaint_id,))

    messages = fetch_all("""
        SELECT *
        FROM complaint_messages

        WHERE complaint_id = %s

        ORDER BY sent_at
    """, (complaint_id,))

    resolutions = fetch_all("""
        SELECT *
        FROM resolutions

        WHERE complaint_id = %s

        ORDER BY cycle_no
    """, (complaint_id,))

    sla = fetch_one("""
        SELECT *
        FROM sla_clocks

        WHERE complaint_id = %s
    """, (complaint_id,))

    sla_events = []

    if sla:
        sla_events = fetch_all("""
            SELECT *
            FROM sla_events

            WHERE sla_id = %s

            ORDER BY event_time
        """, (sla["sla_id"],))

    return {
        "details": complaint,
        "history": history,
        "assignments": assignments,
        "messages": messages,
        "resolutions": resolutions,
        "sla": sla,
        "sla_events": sla_events
    }
