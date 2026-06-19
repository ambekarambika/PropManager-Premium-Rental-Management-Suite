PropManager — Premium Rental Management Suite

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
PropManager/
├── backend/                       # FastAPI REST API Backend
│   ├── routers/                   # Endpoint routers (auth, properties, agreements, payments, etc.)
│   ├── auth.py                    # Token creation, password hashing, and encryption logic
│   ├── database.py                # SQLAlchemy engine initialization and session generator
│   ├── dependencies.py            # API request dependency injectors (current user lookup, JWT guards)
│   ├── main.py                    # FastAPI entrypoint application definition
│   ├── models.py                  # SQLAlchemy Database schema declarations (User, Property, Agreement, Payment)
│   ├── schemas.py                 # Pydantic data serialization & validation schemas
│   ├── seed.py                    # Database seeder to recreate tables and insert initial mock records
│   └── test_db.py                 # Small utility to verify database connectivity
├── frontend/                      # Vanilla Web Client
│   ├── js/
│   │   ├── api.js                 # API wrapper handling backend HTTP fetch + local mock database fallback
│   │   └── app.js                 # App controller coordinating event listeners, rendering views, and state
│   ├── index.html                 # Core single-page application markup shell
│   ├── style.css                  # Global design theme stylesheet
│   ├── property-rental-erd.mermaid# Diagram representation of the database model
│   └── property-rental-management-roadmap.md # Implementation plans and feature roadmap
├── .env                           # Local environment configuration file (Database URL, SECRET_KEY, and expirations)
├── requirements.txt               # Python package dependencies
├── ui_features_backend_mapping.txt # Mapping document linking UI screens to API endpoints and DB operations
└── PropManager.postman_collection.json # Postman API test suite
```

---

## Getting Started

### 1. Mock Mode (Frontend Only)
Double-click `frontend/index.html` (or run a local server like `npx serve`) to test all features immediately using an in-memory browser database. Use the quick-login selector on the login screen to sign in.

### 2. Live API Mode (With Backend & DB)
1. Configure `DATABASE_URL` and `SECRET_KEY` in `.env`.
2. Run `pip install -r requirements.txt` to install dependencies.
3. Seed the database with `python backend/seed.py`.
4. Run the server: `$env:PYTHONPATH="backend"; uvicorn backend.main:app --reload`.
5. Set `const USE_MOCK = false;` in [`frontend/js/api.js`] and open `http://localhost:8000`.

---

## Database Architecture
See [`property-rental-erd.mermaid`] for relationship details:
* **Users**: Accounts with roles (`admin`, `manager`, `tenant`).
* **Properties**: Real estate asset entries.
* **Agreements**: Lease agreements linking tenants to properties.
* **Payments**: Invoices generated relative to active agreements.
