Customer Complaint Management & Resolution System (CCMRS)

A comprehensive, full-stack application designed to track, manage, and resolve customer complaints efficiently. The system provides real-time analytics, SLA tracking, and a detailed timeline of complaint statuses to ensure high customer satisfaction.

📸 Screenshots

(Note: Create a folder named screenshots in the root directory of this project and place your images there using the filenames below for them to render correctly.)

Dashboard Overview

Complaints List & Filtering

Complaint Details & Timeline

Analytics & SLA Monitoring

✨ Features

Frontend:

Interactive Dashboard: Real-time statistics, SLA monitoring panels, and data visualizations.

Complaint Management: Filter, paginate, and view detailed complaint records.

Resolution Tracking: Visual timeline of complaint history and status changes.

API Inspector: Built-in tool for monitoring backend API responses.

Modern UI: Responsive design built with React, Tailwind CSS, and TypeScript.

Backend:

Data Generation Pipeline: Automated generation of mock data for customers, complaints, orders, products, and SLAs.

Database Management: Structured SQL schema for robust data handling.

REST API: Fast and scalable endpoints to serve dashboard analytics, complaint details, and resolution statuses.

🛠️ Tech Stack

Frontend: React, TypeScript, Vite, Tailwind CSS

Backend: Python (FastAPI / Flask)

Database: SQL (Custom generated schema and indexing)

📂 Folder Structure

Customer-Complaint-Management-System/
├── backend/
│   ├── data_generation/    # Scripts to generate mock system data
│   ├── database/           # SQL schemas and index files
│   ├── main.py             # Main backend API application
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/                # React components, pages, services, and utils
│   ├── .env                # Frontend environment variables
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
├── screenshots/            # 📸 Place your screenshot images here!
└── README.md


🚀 Installation & Setup

Prerequisites

Node.js (v16 or higher)

Python (3.8 or higher)

1. Backend Setup

Navigate to the backend directory and install the required Python packages:

cd backend
pip install -r requirements.txt


Start the backend server:

# If using FastAPI:
uvicorn main:app --reload

# If using Flask:
python main.py


(The backend should now be running, typically on http://localhost:8000)

2. Frontend Setup

Open a new terminal window, navigate to the frontend directory, and install the dependencies:

cd frontend
npm install


Configure the environment variables. Ensure the frontend/.env file points to your local backend:

VITE_API_BASE_URL=http://localhost:8000


Start the Vite development server:

npm run dev


3. View the Application

Open your browser and navigate to the URL provided in the terminal (usually http://localhost:5173).

🔌 API Endpoints (Example)

Here is a brief overview of the core API endpoints exposed by the backend:

GET /api/complaints - Fetch a paginated list of all complaints.

GET /api/complaints/{id} - Fetch detailed information and timeline for a specific complaint.

POST /api/complaints - Submit a new customer complaint.

GET /api/dashboard/stats - Retrieve top-level KPIs and SLA metrics for the dashboard.

GET /api/analytics/trends - Fetch chart data for complaint volume over time.