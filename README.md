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

## Next Phase

Phase 4B: add dashboard summary and unified asset timeline APIs to support a premium frontend experience before React implementation.
