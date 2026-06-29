# AssetFlow AI

**Enterprise Intelligent Asset Lifecycle Management Platform**

AssetFlow AI is a full-stack asset operations platform that unifies allocation, transfer, maintenance, health prediction, and executive analytics under a single security-aware console. Built for multi-department organizations, it combines a production-grade FastAPI backend, React operations UI, FT-Transformer health scoring, and optional Ollama-powered narratives.

---

## Table of Contents

1. [Platform Overview](#platform-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Security, Authentication & RBAC](#security-authentication--rbac)
5. [AI & Machine Learning](#ai--machine-learning)
6. [Reports & Analytics](#reports--analytics)
7. [Operations & Notifications](#operations--notifications)
8. [Project Structure](#project-structure)
9. [Getting Started](#getting-started)
10. [Configuration](#configuration)
11. [API Reference](#api-reference)
12. [Testing & Quality](#testing--quality)
13. [Demo Walkthrough](#demo-walkthrough)
14. [Roadmap & Future Enhancements](#roadmap--future-enhancements)

---

## Platform Overview

### Core capabilities (implemented)

| Module | Description |
|--------|-------------|
| **Operations Center** | Attention queue, live activity feed, fleet KPIs, My Workspace, AI recommendations, pipeline status |
| **Asset Lifecycle** | Register, assign, transfer, maintain, health snapshots, unified timeline, QR scan |
| **Organization** | Departments, employees, role-linked user accounts |
| **Maintenance Center** | Fleet-wide maintenance visibility and per-asset records |
| **Intelligence** | FT-Transformer batch scoring, drift detection, maintenance recommendations, root-cause analysis |
| **AI Assistant** | Tool-routed natural-language queries with optional Ollama formatting |
| **Reports & Analytics** | Executive AI report, health drift, cost optimization, replacement planning, maintenance schedule |
| **Notifications** | Department-scoped alerts, header bell, mark-read workflows |
| **Auth & Admin** | JWT login, forced password change, user provisioning, role management |

### Design principles

- **Layered backend** — API → Service → Repository → PostgreSQL
- **Department scoping** — Non-admin users see only their department's operational data
- **Grounded AI** — Predictions and assistant answers are backed by database facts and ML artifacts
- **Staged UX** — Reports load template analytics first, then Ollama enhancement in the background
- **Enterprise RBAC** — Three roles (Admin, Manager, Viewer) with least-privilege defaults

---

## Technology Stack

| Layer | Technologies |
|-------|----------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2 |
| **Database** | PostgreSQL |
| **Frontend** | React 18, TypeScript, Vite, TanStack Query, Tailwind CSS, Recharts |
| **ML** | PyTorch FT-Transformer (`ml/`), feature engineering pipeline |
| **LLM (optional)** | Ollama (`llama3.2:3b` default) for narrative enhancement |
| **Auth** | JWT (HS256), bcrypt password hashing |
| **Testing** | pytest, FastAPI TestClient |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                        │
│  Operations │ Assets │ Maintenance │ Reports │ Assistant │ Auth  │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST /api/v1
┌────────────────────────────▼────────────────────────────────────┐
│                      FastAPI Application                         │
│  ┌──────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │ Auth/RBAC│  │ Access Scope │  │ Request Logging /ready  │  │
│  └──────────┘  └──────────────┘  └─────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Services: Dashboard, Prediction, Reports Analytics,     │   │
│  │ Drift, Cost, Replacement, Pipeline, Assistant, Workspace  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Repositories → SQLAlchemy Models → PostgreSQL             │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
   PostgreSQL          ml/artifacts/          Ollama (optional)
   (operational)       (FT-Transformer)       (narratives)
```

**Entry points**

- Backend: [`app/main.py`](app/main.py)
- API router: [`app/api/v1/router.py`](app/api/v1/router.py)
- Frontend: [`frontend/src/main.tsx`](frontend/src/main.tsx)

---

## Security, Authentication & RBAC

### Roles

| Role | Scope | Key permissions |
|------|-------|-----------------|
| **ADMIN** | Organization-wide | Full CRUD, user management, AI pipeline, org-wide reports |
| **MANAGER** | Own department | Asset/maintenance writes, AI pipeline, department reports |
| **VIEWER** | Own department | Read-only assets/maintenance/reports; AI narratives load passively |

### Access control

- JWT bearer tokens with configurable expiry (`JWT_EXPIRE_MINUTES`)
- Forced password change on first login (`must_change_password`)
- Unique temporary passwords per seeded user (printed during seed)
- Department scoping via [`app/core/access_scope.py`](app/core/access_scope.py)
- API write guards in [`app/core/permissions.py`](app/core/permissions.py)

### Reports visibility (by design)

- **Admin** — Organization-wide report; full department comparison charts
- **Manager / Viewer** — `{Department} department report` only
- **Viewers** — Cannot run AI Scoring; receive AI-enhanced narratives automatically when Ollama is available
- **Managers / Admins** — AI Enhanced toggle + Run AI Scoring on Reports and Dashboard

Non-admin users receive **anonymous org benchmark KPIs** (company avg health, dept vs company delta, company high-risk count) without exposing other departments' asset identifiers.

---

## AI & Machine Learning

### FT-Transformer health model

- Trained on synthetic + seeded operational features (`ml/`)
- Batch scoring via `POST /intelligence/score-batch`
- Outputs: health score (0–1), risk level (LOW/MEDIUM/HIGH), confidence, feature explanations
- Predictions cached in-memory and optionally persisted to `asset_health_history`

### Autonomous intelligence pipeline

`POST /operations/pipeline/run` executes:

1. **Batch scoring** — FT-Transformer inference for all active assets
2. **Drift detection** — Compares current vs previous health scores
3. **Policy automation** — Auto-schedules maintenance where rules apply
4. **Notifications** — Creates drift, escalation, and positive-change alerts

Optional background scheduler (`SCHEDULER_ENABLED`) runs the pipeline on an interval.

### AI Assistant

- Intent routing + grounded tool execution ([`app/services/assistant_service.py`](app/services/assistant_service.py))
- Optional Ollama layer for polished natural-language responses
- Template fallback when Ollama is unavailable or validation fails
- Supports fleet queries: maintenance priorities, high-risk assets, transfers, counts by type

### Ollama configuration

```env
ASSISTANT_USE_OLLAMA=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TIMEOUT_SECONDS=30
```

Pull the model: `ollama pull llama3.2:3b`

---

## Reports & Analytics

Unified endpoint: `GET /operations/reports/analytics?use_ai=true|false`

### Executive AI Report (11 sections)

1. Executive Summary  
2. Overall Fleet Health  
3. Major Events This Week  
4. Assets Requiring Immediate Attention  
5. Maintenance Performance  
6. Department-wise Performance  
7. AI Observations  
8. Risk Analysis  
9. Predicted Issues  
10. Recommended Actions  
11. Expected Impact Next Week  

### Operational report sections

| Section | Includes |
|---------|----------|
| **Health Drift** | Trend charts, deteriorating vs improving counts, AI interpretation, key factors |
| **Cost Optimization** | TCO distribution, department spend charts, savings estimates, AI recommendations |
| **Replacement Planning** | Per-asset reasoning: why replace, remaining life, health trend, repair vs replace, delay impact |
| **Maintenance Schedule** | Priority ranking, department workload, skip-risk analysis, schedule table |

### UX behavior

- **Staged loading** — Template analytics appear in seconds; Ollama enhancement runs in background (up to 120s)
- **AI Enhanced toggle** — Admin/Manager only; Viewers consume AI narratives passively
- **Pipeline feedback** — Post-run summary: assets scored, drift alerts, notifications created
- **Source indicator** — Shows whether content came from Ollama or analyst templates

---

## Operations & Notifications

- **My Workspace** — Assigned assets, upcoming maintenance, personal notifications (`GET /dashboard/my-workspace`)
- **Notifications bell** — Header badge with unread count; department-scoped
- **Drift monitoring** — Configurable thresholds (`DRIFT_MIN_DROP`, `DRIFT_SEVERE_DROP`, etc.)
- **Knowledge graph API** — Asset neighborhood and department high-risk graph endpoints
- **Health endpoints** — `GET /health` (liveness), `GET /ready` (DB + ML model readiness)

---

## Project Structure

```
AssetFlow-AI/
├── app/                          # FastAPI backend
│   ├── api/                      # Routers, deps, auth
│   │   └── v1/endpoints/         # REST endpoints by domain
│   ├── core/                     # Config, DB, RBAC, access scope, security
│   ├── models/                   # SQLAlchemy ORM models
│   ├── repositories/             # Data access layer
│   ├── schemas/                  # Pydantic request/response models
│   ├── services/                 # Business logic & AI services
│   ├── seeding/                  # Demo/ML dataset generators
│   ├── middleware/               # Request logging
│   └── main.py                   # Application entrypoint
├── frontend/                     # React + TypeScript SPA
│   └── src/
│       ├── app/                  # Router, layout shell, breadcrumbs
│       ├── features/             # Domain modules (auth, assets, reports, …)
│       ├── pages/                # Route-level page wrappers
│       └── shared/               # UI primitives, API client, utilities
├── ml/                           # FT-Transformer training & inference
├── alembic/                      # Database migrations
├── tests/                        # pytest suite
├── scripts/dev/                  # Manual dev/diagnostic scripts
├── docs/                         # Demo script, architecture reference, DB schema
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

### Frontend feature modules

| Path | Purpose |
|------|---------|
| `features/auth/` | Login, permissions, password change, My Workspace types |
| `features/dashboard/` | Operations Center components |
| `features/assets/` | Asset registry, detail, lifecycle, health report |
| `features/maintenance/` | Maintenance center |
| `features/departments/` | Department CRUD |
| `features/employees/` | Employee CRUD |
| `features/reports/` | Reports & Analytics page, Recharts |
| `features/intelligence/` | AI recommendations panel |
| `features/operations/` | Notifications, pipeline, reports API hooks |
| `features/assistant/` | Chat assistant panel |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- (Optional) Ollama for LLM narratives

### 1. Clone and install

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt   # for tests

cd frontend && npm install && cd ..
```

### 2. Environment

```bash
cp .env.example .env
# Edit DATABASE_URL, JWT_SECRET_KEY, Ollama settings
```

### 3. Database

```bash
py -m alembic upgrade head
py -m app.seeding --profile demo --reset
```

Seeded accounts use unique temporary passwords printed to the console. Change password on first login.

| Profile | Assets | History | Use case |
|---------|--------|---------|----------|
| `minimal` | 30 | 30 days | Quick dev / CI |
| `demo` | 200 active + 20 inactive | 18 months | Default demo & evaluation |
| `ml` | 200 | 18 months + dense health | ML training prep |

### 4. Run (Windows PowerShell)

```powershell
# Terminal 1 — Backend
$env:PYTHONPATH='.'; py -m uvicorn app.main:app --port 8000 --reload

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open **http://localhost:5173** → login with seeded credentials.

### 5. Verify

- API docs: http://127.0.0.1:8000/docs  
- Health: http://127.0.0.1:8000/health  
- Readiness: http://127.0.0.1:8000/ready  

### Dev tips (Windows)

- Frontend uses port **5173** (`strictPort: true`). If busy: `netstat -ano | findstr :8000` then `taskkill /PID <pid> /F`
- Vite cache is stored outside OneDrive (`%TEMP%\vite-cache-assetflow`) to avoid file-lock errors

---

## Configuration

See [`.env.example`](.env.example) for all options. Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | PostgreSQL connection string |
| `AUTH_ENABLED` | `true` | Enable JWT authentication |
| `ML_ENABLED` | `true` | Enable FT-Transformer inference |
| `ASSISTANT_USE_OLLAMA` | `true` | Use Ollama for LLM narratives |
| `SCHEDULER_ENABLED` | `false` | Background AI pipeline scheduler |
| `POLICY_AUTOMATION_ENABLED` | `true` | Auto-maintenance policy rules |
| `DEBUG` | `false` | Verbose logging |

---

## API Reference

Base path: `/api/v1`

### Auth

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Obtain JWT |
| GET | `/auth/me` | Current user profile |
| POST | `/auth/change-password` | Change password |
| GET/POST/PATCH | `/auth/users` | User admin (Admin only) |

### Core domains

- `/departments`, `/employees` — Organization
- `/assets`, `/allocations`, `/transfers`, `/maintenance`, `/health-history` — Asset lifecycle
- `/dashboard/summary`, `/dashboard/my-workspace` — Operations metrics
- `/intelligence/*` — Scoring, recommendations, root cause
- `/assistant/chat` — AI assistant
- `/operations/*` — Pipeline, notifications, drift, reports, cost, replacement, maintenance schedule

Full interactive documentation: **http://127.0.0.1:8000/docs**

---

## Testing & Quality

```bash
# Unit tests (no DB required)
py -m pytest tests/ -m "not integration" -q

# Integration tests (requires PostgreSQL)
py -m pytest tests/ -m integration -q

# Assistant routing (dev script)
py scripts/dev/test_routing.py
```

| Test file | Coverage |
|-----------|----------|
| `test_access_scope.py` | Department scoping rules |
| `test_permissions.py` | API RBAC matrix |
| `test_password_policy.py` | Password generation & validation |
| `test_reports_analytics_benchmarks.py` | Org benchmarks & scoped predictions |
| `test_auth_integration.py` | End-to-end auth flows (integration) |
| `test_health.py` | Liveness endpoint |

---

## Demo Walkthrough

See **[docs/DEMO.md](docs/DEMO.md)** for a 5-minute scripted demo including:

- Operations Center and AI scoring
- Asset lifecycle on `IT-LAP-0001`
- Assistant queries
- Organization management

---

## Roadmap & Future Enhancements

The following items are identified for subsequent releases:

### Reports & analytics

- [ ] Dedicated **Asset Health Reports** and **Department Reports** sub-pages (currently embedded in unified analytics)
- [ ] **Post-scoring diff panel** — highlight assets whose health scores changed after pipeline runs
- [ ] **Risk heatmaps** and interactive trend timelines across the fleet
- [ ] **Prediction confidence** and risk-trend-over-time in Health Drift
- [ ] **Key contributing factors** with deeper SHAP-style explanations per asset
- [ ] Richer repair-vs-replace **lifecycle cost modeling** in Replacement Planning

### AI & platform

- [ ] Optional **Executive Viewer** role (org-wide read-only without Admin write access)
- [ ] Stronger Ollama JSON reliability for all 11 executive sections in a single pass
- [ ] Docker Compose deployment profile for one-command local/staging environments
- [ ] SSE/WebSocket live updates for pipeline completion across Dashboard and Reports
- [ ] Export to PDF/Excel for executive reports

### Enterprise hardening

- [ ] Audit log for admin actions and pipeline runs
- [ ] SSO / OIDC integration
- [ ] Rate limiting and API key support for integrations

---

## Additional Documentation

| Document | Description |
|----------|-------------|
| [docs/DEMO.md](docs/DEMO.md) | 5-minute demo script |
| [docs/FRONTEND_ARCHITECTURE.md](docs/FRONTEND_ARCHITECTURE.md) | Frontend product architecture blueprint |
| [docs/database/reference_schema.sql](docs/database/reference_schema.sql) | Reference SQL schema (Alembic is source of truth) |
| [ml/README.md](ml/README.md) | ML training and artifact pipeline |
| [scripts/dev/README.md](scripts/dev/README.md) | Manual dev/diagnostic scripts |

---

## License & Attribution

Academic / enterprise evaluation project — AssetFlow AI Intelligent Asset Lifecycle Management System.
