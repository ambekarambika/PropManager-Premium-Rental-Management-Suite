# PropManager — Premium Rental Management Suite

Welcome to **PropManager**, a premium, state-of-the-art property rental management system designed for property owners, administrators, and tenants. It features a modern, visually stunning web interface complete with high-end glassmorphism design elements, real-time interactive dashboards, a comprehensive rental ledger, lease agreements management, and a tenant booking request workflow.

The project is structured as a monorepo consisting of:
*   **Frontend**: A single-page application built with Vanilla HTML5, CSS3, and JavaScript (ES6 Modules) using responsive design, smooth animations, and a rich dark mode.
*   **Backend**: A REST API built with **FastAPI** (Python), **SQLAlchemy ORM**, and **PostgreSQL** database hosting.

---

## Key Features

*   **Role-Based Access Control (RBAC)**: Distinct dashboards and permissions for **Administrators**, **Property Managers**, and **Tenants**.
*   **Beautiful Dashboard Interface**: Dynamic widgets showcasing rent collected, vacant vs. occupied ratios, open maintenance tickets, and recent activity logs.
*   **Property Portfolio Management (CRUD)**: Manage properties, update specifications (rent, type, bedrooms, bathrooms), and track status (`vacant`, `occupied`, `maintenance`).
*   **Tenant Management**: Onboard tenants, link profiles, and specify emergency contacts.
*   **Rental Agreements**: Create, renew, and terminate lease agreements between tenants and properties. Includes constraints to prevent double-leasing.
*   **Rent Ledger & Payments**: Monitor invoices and transaction status (`paid`, `pending`, `overdue`), and log settled payment methods (UPI, Net Banking, Cash, Cheque).
*   **Tenant Booking Workflow**: Tenants can request bookings directly for vacant properties. Managers can view and approve booking requests, which automatically updates the property occupancy, registers a lease agreement, and populates the rent ledger.
*   **Dual Mode Capability (Mock vs. Live API)**: Built-in local storage mock database to run and test the complete frontend instantly in the browser without any database configuration, with an easy switch to connect to a live backend.

---

## Tech Stack

### Frontend
*   **Languages**: HTML5, CSS3, JavaScript (ES6)
*   **Styling**: Premium custom CSS system featuring modern CSS variables, vibrant color schemes, glassmorphic card overlays, responsive layouts, hover animations, and smooth transitions.
*   **Icons**: Tabler Icons CDN
*   **Fonts**: Inter / Outfit via Google Fonts

### Backend
*   **Framework**: FastAPI (Python 3.8+)
*   **Database ORM**: SQLAlchemy
*   **Database Driver**: `psycopg2-binary` (PostgreSQL client)
*   **Authentication & Security**: JWT bearer authentication via `python-jose`, passwords hashed with `passlib` (using bcrypt).

---

## Project Structure

```
New folder/
├── backend/                       # FastAPI REST API Backend
│   ├── routers/                   # Endpoint routers (auth, properties, agreements, payments, etc.)
│   ├── auth.py                    # Token creation, password hashing, and encryption logic
│   ├── database.py                # SQLAlchemy engine initialization and session generator
│   ├── dependencies.py            # API request dependency injectors (current user lookup, JWT guards)
│   ├── main.py                    # FastAPI entrypoint application definition
│   ├── models.py                  # SQLAlchemy Database schema declarations (User, Property, Agreement, Payment)
│   ├── schemas.py                 # Pydantic data serialization & validation schemas
│   └── test_db.py                 # Small utility to verify database connectivity
├── frontend/                      # Vanilla Web Client
│   ├── js/
│   │   ├── api.js                 # API wrapper handling backend HTTP fetch + local mock database fallback
│   │   └── app.js                 # App controller coordinating event listeners, rendering views, and state
│   ├── index.html                 # Core single-page application markup shell
│   ├── style.css                  # Global design theme stylesheet
│   └── property-rental-erd.mermaid# Diagram representation of the database model
├── requirements.txt               # Python package dependencies
└── PropManager.postman_collection.json # Postman API test suite
```

---

## Getting Started

### 1. Running the Frontend (Zero Configuration Setup)

The frontend includes an **In-Memory Mock Database** that runs inside your browser (`localStorage`). This allows you to evaluate, demo, and test every single feature immediately without setting up databases or running servers.

1.  Navigate into the `frontend/` directory.
2.  Open `index.html` in your web browser (you can double-click it, use VS Code "Live Server", or run a simple local server like `npx serve` or `python -m http.server`).
3.  Use the **Quick Role Selector** overlay on the login screen to sign in instantly with mock accounts:
    *   **Property Manager**: Rajesh Kumar (`rajesh@example.com` / `password`)
    *   **Administrator**: Super Admin (`admin@example.com` / `password`)
    *   **Tenant**: Arjun Sharma (`arjun@example.com` / `password`)

---

### 2. Setting Up the Backend & Live API Mode

If you wish to run the live Python FastAPI backend and connect the frontend to it, follow these steps:

#### Backend Setup
1.  Ensure you have **Python 3.8+** installed.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the FastAPI development server:
    ```bash
    uvicorn backend.main:app --reload
    ```
    The server will spin up and run on [http://localhost:8000](http://localhost:8000). The tables will automatically be created on database startup. You can view the automated OpenAPI interactive documentation at `http://localhost:8000/docs`.

#### Connecting the Frontend to the Backend
1.  Open `frontend/js/api.js` in your text editor.
2.  Change line 4 to set `USE_MOCK` to `false`:
    ```javascript
    const USE_MOCK = false; // Set to false to connect to your live Python backend
    ```
3.  Refresh the frontend index page in the browser. It will now fire requests directly to the FastAPI server running on `http://localhost:8000`.

---

## Database Architecture

A representation of the relationship model is defined below. The relationships are also documented in detail in the [property-rental-erd.mermaid] file:

*   **Users**: Base profile container holding name, email, credentials, and access tier (`admin`, `manager`, `tenant`).
*   **Properties**: Real estate asset entries belonging to an owner/manager, featuring standard address, pricing, and structural specifications.
*   **Agreements**: Formal contracts linking a User (Tenant) to a specific Property over a date range. Built-in database rules guarantee that a property can have at most one active lease agreement at any point in time.
*   **Payments**: Invoices generated relative to active lease agreements. Tracks outstanding bills and completed logs.
