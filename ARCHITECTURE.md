# System Architecture

## 1. Project Overview

The Customer Complaint Management & Resolution System is designed to manage customer complaints, track their lifecycle, monitor SLA compliance, and provide analytical insights into complaint resolution operations.

The application follows a frontend-backend architecture with PostgreSQL as the primary database.

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| UI Styling | Tailwind CSS |
| Charts | Recharts |
| API Communication | Axios |
| Backend | Python, FastAPI |
| Database | Neon PostgreSQL |
| Database Driver | pg8000 |
| API Documentation | Swagger / OpenAPI |

## 3. High-Level Architecture

```text
             USER
               |
               v
      REACT FRONTEND
       (Vite + TS)
               |
               | HTTP REST API
               v
        FASTAPI BACKEND
               |
               | Database Queries
               v
       DATABASE CONNECTION
          (pg8000)
               |
               v
       NEON POSTGRESQL
               |
     -----------------------
     |          |          |
     v          v          v
 Complaints  Customers   Agents
     |
     v
 Related Tables
     |
     |-- Complaint Messages
     |-- Complaint Assignments
     |-- Status History
     |-- Resolutions
     |-- SLA Clocks
     |-- SLA Events
     |-- Surveys
```

## 4. Backend Architecture

The backend is implemented using FastAPI and organized around REST API endpoints.

The application uses a shared database connection module:

`data_generation/db_connection.py`

Database operations are performed using the `pg8000` driver.

The current API includes:

### Dashboard APIs
- `/api/dashboard/summary`
- `/api/dashboard/status`
- `/api/dashboard/priority`
- `/api/dashboard/severity`
- `/api/dashboard/sla`

### Analytics APIs
- `/api/analytics/categories`
- `/api/analytics/agents`

### Complaint APIs
- `/api/complaints`
- `/api/complaints/{complaint_id}`

### Health API
- `/api/health`

## 5. Database Architecture

The PostgreSQL database maintains complaint information and its related operational records.

Main entities include:

- Customers
- Complaints
- Agents
- Teams
- Complaint Messages
- Complaint Assignments
- Complaint Status History
- Resolutions
- SLA Clocks
- SLA Events
- Surveys

The complaint record acts as the central entity connecting customer information, assignments, communication history, resolution records, and SLA tracking.

## 6. Complaint Lifecycle

The system tracks complaint statuses through the following lifecycle:

```text
OPEN
  |
  v
CLASSIFIED
  |
  v
ASSIGNED
  |
  v
IN_PROGRESS
  |
  +------> WAITING_FOR_CUSTOMER
  |                  |
  |                  v
  +--------------> IN_PROGRESS
  |
  v
RESOLVED
  |
  v
CLOSED
```

Complaints may also be escalated or reopened depending on their lifecycle events.

## 7. SLA Monitoring

The system maintains SLA information through:

- Response deadlines
- Resolution deadlines
- First response timestamps
- Resolution timestamps
- Response breach indicators
- Resolution breach indicators
- SLA pause information
- SLA event history

Dashboard APIs aggregate this information to provide SLA compliance insights.

## 8. Frontend Architecture

The React frontend consumes the existing FastAPI REST endpoints.

Main application modules:

- Dashboard
- Complaint Management
- Complaint Details
- Analytics

The frontend uses Axios for API communication and Recharts for analytical visualizations.

## 9. API Documentation

Interactive API documentation is available through FastAPI Swagger UI:

`http://127.0.0.1:8000/docs`

## 10. Data Flow

1. The user opens the React application.
2. The frontend sends HTTP requests to FastAPI.
3. FastAPI processes the request and executes SQL queries.
4. The database connection retrieves records from Neon PostgreSQL.
5. FastAPI returns JSON responses.
6. React renders the retrieved information through dashboard cards, tables, charts, and complaint details.

## 11. Current Scope

The current backend exposes read-only GET endpoints for dashboard reporting, analytics, complaint search, and complaint details.

Complaint creation, assignment updates, status changes, messaging, and resolution operations require additional APIs and are not included in the current API implementation.