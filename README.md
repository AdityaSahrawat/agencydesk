# AgencyDesk — Multi-Tenant SaaS Platform

AgencyDesk is a production-ready, multi-tenant client & project management platform built for digital agencies, software teams, and client portals. A single deployment serves multiple agencies while maintaining **strict data isolation** and **role-based access control (RBAC)** across tenants.

---

## 🌟 Key Features

- **Multi-Tenant Isolation**: Every API request is strictly scoped by `X-Agency-ID` headers and database query boundaries.
- **Role-Based Access Control (RBAC)**:
  - `agency_admin`: Full management of agency settings, clients, team members, projects, and tasks.
  - `agency_member`: Project management, task creation, status updates, file uploads, and time logging.
  - `client_user`: Restricted client portal view allowing access only to assigned company projects, tasks, and client-visible files.
- **Client & Project Management**: Track client organizations, active/planning projects, deadlines, and team assignments.
- **Kanban & Task Workflow**: Assign tasks, set priorities, track due dates, and update task statuses.
- **Internal Privacy Controls**: Flag tasks, comments, and files as `internal` to automatically hide sensitive internal notes from client portal users.
- **File Management & Approval**: Upload task attachments with approval workflow statuses (`pending`, `approved`, `needs_changes`).
- **Time Logging & Reporting**: Log billable hours per task and track total project hours.
- **Sleek Modern UI**: Built with Next.js App Router, Tailwind CSS v4, and Shadcn UI components.

---

## 🛠️ Tech Stack

### Backend (`be/`)
- **Python 3.14+**
- **FastAPI** (Async Web Framework)
- **SQLAlchemy 2.0 ORM** (Async Engine with `asyncpg`)
- **PostgreSQL 16**
- **Pydantic v2** & `pydantic-settings`
- **Alembic** (Database Migrations)
- **PyJWT & bcrypt** (Authentication)
- **uv** (Fast Python package manager)
- **Docker & Docker Compose**

### Frontend (`fe/`)
- **Next.js 16** (App Router & Turbopack)
- **React 19**
- **TypeScript 5**
- **Tailwind CSS v4** (`@tailwindcss/postcss`)
- **TanStack React Query v5**
- **Lucide React** (Icons) & **Sonner** (Toast Notifications)
- **Shadcn UI** Components

---

## 🚀 Quick Start

### Option 1: Running with Docker Compose (Recommended)

1. **Start all services (PostgreSQL + FastAPI Backend)**:
   ```bash
   cd be
   docker compose up --build
   ```
   *(Migrations and seed data run automatically on startup!)*

2. **Start the Next.js Frontend**:
   ```bash
   cd fe
   npm run dev
   ```

3. Open **`http://localhost:3000`** in your browser.

---

### Option 2: Running Locally without Docker

#### 1. Backend Setup (`be/`)
Ensure PostgreSQL is running locally on port `5432` with database `agencydesk`.

```bash
cd be

# Run migrations, seed demo data, and start dev server
make dev
```
The FastAPI backend will start on **`http://localhost:8000`** (interactive API docs available at `http://localhost:8000/docs`).

#### 2. Frontend Setup (`fe/`)
```bash
cd fe
npm install
npm run dev
```
The Next.js frontend will start on **`http://localhost:3000`**.

---

## 🔐 Pre-Seeded Demo Accounts

Click any demo button on the login screen or enter these credentials:

| Role | Email | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Agency Admin** | `alice@agencyalpha.com` | `Password123!` | Full Agency Administration (`/agency/dashboard`) |
| **Agency Member** | `bob@agencyalpha.com` | `Password123!` | Team Member Workspace (`/agency/dashboard`) |
| **Client Portal User** | `john@gmail.com` | `Password123!` | Client Portal (`/portal`) |

---

## 📂 Project Structure

```
agencydesk/
├── be/                       # FastAPI Backend
│   ├── alembic/              # Database migration scripts
│   ├── app/
│   │   ├── api/v1/           # REST API Endpoints (Auth, Clients, Projects, Tasks, etc.)
│   │   ├── core/             # Core Config, Security, JWT, Dependencies, Exceptions
│   │   ├── db/               # Async Engine, Base Models, Sessions
│   │   ├── models/           # SQLAlchemy ORM Models
│   │   ├── repositories/     # Tenant-Scoped Data Repositories
│   │   ├── schemas/          # Pydantic Request/Response Schemas
│   │   └── services/         # Business Logic Layer
│   ├── seed.py               # Seed script for demo accounts & sample workspace data
│   ├── Makefile              # Helper commands (make dev, make migrate, make seed)
│   ├── Dockerfile            # Container definition
│   └── docker-compose.yml    # Service orchestration (Backend + Postgres)
│
└── fe/                       # Next.js Frontend
    ├── app/                  # Next.js App Router
    │   ├── (auth)/login/     # Login Page with glassmorphism UI
    │   ├── (dashboard)/
    │   │   ├── agency/       # Agency Workspace (Dashboard, Clients, Projects, Tasks, Users, Settings)
    │   │   └── portal/       # Client Portal (Projects, Tasks, Files)
    ├── components/           # UI & Layout Components (Navbar, Sidebars, Data Tables, Badges)
    ├── hooks/                # TanStack Query custom hooks (use-api.ts)
    ├── providers/            # AuthProvider & QueryClientProvider
    └── services/             # Axios API Client (api.ts)
```

---

## 📡 API Endpoints Summary

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/auth/login` | `POST` | Authenticate user & receive JWT tokens |
| `/api/v1/auth/me` | `GET` | Get authenticated user profile & memberships |
| `/api/v1/clients` | `GET / POST` | List & create clients for current agency |
| `/api/v1/projects` | `GET / POST` | List & create projects (filtered by membership/role) |
| `/api/v1/tasks` | `GET / POST` | List & create tasks with priority, due date & status |
| `/api/v1/tasks/{id}/status` | `PATCH` | Update task status (`todo`, `doing`, `done`) |
| `/api/v1/comments` | `GET / POST` | Task comments (filtered for client visibility) |
| `/api/v1/files/upload` | `POST` | Upload file attachments |
| `/api/v1/time-entries` | `GET / POST` | Log hours worked on tasks/projects |
| `/api/v1/dashboard/summary` | `GET` | Aggregated dashboard metrics & task counters |

---

## 🧪 Testing

Run backend test suite:
```bash
cd be
make test
```

Run frontend type check & production build verification:
```bash
cd fe
npx tsc --noEmit
npm run build
```

---

## 📄 License

This project is licensed under the MIT License.
