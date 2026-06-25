# AssetFlow AI

Intelligent Asset Lifecycle Management System focused on tracking assets across allocation, transfer, maintenance, and health history workflows.

## Current Status

- Backend foundation is implemented with FastAPI + PostgreSQL + SQLAlchemy + Alembic.
- Core business APIs are available and manually validated.
- Frontend, authentication, automated tests, Docker, and AI pipeline are planned for upcoming phases.

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy 2.x
- Alembic
- Pydantic v2

## Architecture

Layered backend architecture:

1. API routers (`app/api/v1/endpoints`)
2. Service layer (`app/services`)
3. Repository layer (`app/repositories`)
4. Models and database (`app/models`, PostgreSQL)

Main entrypoint: `app/main.py`

## Quick Start (Local)

### 1) Clone and install dependencies

```bash
pip install -r requirements.txt
```

### 2) Configure environment

Create `.env` from `.env.example` and set your PostgreSQL credentials:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/assetflow_ai
APP_NAME=AssetFlow AI
DEBUG=true
```

### 3) Create database and run migration

```bash
alembic upgrade head
```

### 4) Run the API server

```bash
uvicorn app.main:app --reload
```

### 5) Open docs

- Swagger UI: `http://127.0.0.1:8000/docs`
- Redoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

## API Contract Inventory (Phase 4A)

Base path: `/api/v1`

### Departments

- `POST /departments`
- `GET /departments`
- `GET /departments/{department_id}`
- `PATCH /departments/{department_id}`
- `DELETE /departments/{department_id}`

### Employees

- `POST /employees`
- `GET /employees`
- `GET /employees/{employee_id}`
- `PATCH /employees/{employee_id}`
- `DELETE /employees/{employee_id}`

### Asset Lookups

- `GET /asset-categories`
- `GET /asset-types`

### Assets

- `POST /assets`
- `GET /assets`
- `GET /assets/search`
- `GET /assets/{asset_id}`
- `PATCH /assets/{asset_id}`
- `DELETE /assets/{asset_id}`

### Asset Allocations

- `POST /assets/{asset_id}/allocations/assign`
- `POST /assets/{asset_id}/allocations/return`
- `POST /assets/{asset_id}/allocations/reassign`
- `GET /assets/{asset_id}/allocations`
- `GET /employees/{employee_id}/allocations`

### Asset Transfers

- `POST /assets/{asset_id}/transfers`
- `GET /assets/{asset_id}/transfers`

### Maintenance

- `POST /assets/{asset_id}/maintenance`
- `GET /assets/{asset_id}/maintenance`
- `GET /maintenance/{record_id}`
- `PATCH /maintenance/{record_id}`

### Asset Health History

- `POST /assets/{asset_id}/health-history`
- `GET /assets/{asset_id}/health-history`

### Dashboard

- `GET /dashboard/summary`

### Asset Timeline

- `GET /assets/{asset_id}/timeline`

## Data Model Coverage

Core entities currently in schema:

- Departments
- Employees
- Asset Categories
- Asset Types
- Assets
- Asset Allocations (history)
- Asset Transfers (history)
- Maintenance Records (history)
- Asset Health History

## CORS Configuration

The API currently allows local frontend origins:

- `http://localhost:5173`
- `http://127.0.0.1:5173`
- `http://localhost:3000`
- `http://127.0.0.1:3000`

Configured in `app/main.py`.

## Seed Data (Phase 5.5)

Reproducible demo datasets for development and FYP demonstrations:

```bash
py -m alembic upgrade head
py -m app.seeding --profile demo --reset
```

| Profile | Assets | History | Use |
|---------|--------|---------|-----|
| `minimal` | 30 | 30 days | Quick dev / CI |
| `demo` | 200 active + 20 inactive | 18 months | Default — Operations Center + FYP |
| `ml` | 200 | 18 months + dense health | FT-Transformer prep |

The demo profile includes fixed asset tags for walkthroughs: `IT-LAP-0001`, `OPS-VAN-001`, `SRV-PROD-01`, `ADM-PRT-001`. See [DEMO.md](DEMO.md).

## Frontend (Phases 5A–6A)

A frontend workspace is available at `frontend/` with:

- React + TypeScript + Vite
- TanStack Query provider with toast notifications
- App shell with sidebar/header/breadcrumb routing
- **Operations Center** — attention queue, live activity feed, compact metrics, charts
- **Assets** — search, filters, CRUD, URL-driven params
- **Asset Detail** — hero, tabs, lifecycle actions, timeline
- **Maintenance Center** — assets in maintenance + due count
- **Departments & Employees** — CRUD + allocation history

See [DEMO.md](DEMO.md) for a 5-minute walkthrough script.

Run locally (backend and frontend together):

```bash
# Terminal 1 — backend
py -m uvicorn app.main:app --reload

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173/dashboard`. Optional: copy `frontend/.env.example` to `frontend/.env` to override `VITE_API_BASE_URL`.

**Dev tips (Windows):**

- Frontend must run on port **5173** (`strictPort: true` in Vite config). If port 5173 is busy, stop other Node processes: `taskkill /F /IM node.exe`, then restart `npm run dev`.
- Vite cache is stored outside OneDrive (`%TEMP%\vite-cache-assetflow`) to avoid file-lock errors.
- Backend CORS allows localhost ports 5173, 5174, and 3000.
