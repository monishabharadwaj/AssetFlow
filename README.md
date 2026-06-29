# AssetFlow AI

**Enterprise Intelligent Asset Lifecycle Management Platform**

AssetFlow AI is a full-stack platform for organizations that manage physical and IT assets across departments. It tracks the complete asset lifecycle—from procurement and allocation through maintenance, health monitoring, and replacement planning—while layering **machine-learning health predictions**, **autonomous drift monitoring**, and **AI-generated executive analytics** on top of operational data.

The system is designed for **multi-department enterprises**: each department owns a fleet of assets, managers operate within their scope, and organization administrators see the full picture. Security is enforced through **JWT authentication**, **role-based access control (RBAC)**, and **department-level data scoping** on every sensitive endpoint.

---

## Table of Contents

1. [What This Project Does](#what-this-project-does)
2. [Problem Statement & Solution](#problem-statement--solution)
3. [Key Features by Module](#key-features-by-module)
4. [User Roles & Access Model](#user-roles--access-model)
5. [Technology Stack](#technology-stack)
6. [System Architecture](#system-architecture)
7. [Data Flow Diagrams](#data-flow-diagrams)
8. [AI & Machine Learning Pipeline](#ai--machine-learning-pipeline)
9. [Reports & Executive Analytics](#reports--executive-analytics)
10. [Database & Domain Model](#database--domain-model)
11. [Complete Project Structure](#complete-project-structure)
12. [Getting Started](#getting-started)
13. [Configuration Reference](#configuration-reference)
14. [API Reference](#api-reference)
15. [Testing & Quality Assurance](#testing--quality-assurance)
16. [Demo & Evaluation](#demo--evaluation)
17. [Roadmap & Future Enhancements](#roadmap--future-enhancements)
18. [Additional Documentation](#additional-documentation)

---

## What This Project Does

AssetFlow AI answers four questions that asset-intensive organizations face daily:

| Question | How AssetFlow AI answers it |
|----------|----------------------------|
| **Where are our assets and who has them?** | Asset registry, allocation history, transfers, QR scan, unified timeline |
| **Are they healthy and when will they fail?** | FT-Transformer health scores, risk levels, drift alerts, root-cause analysis |
| **What maintenance should we do and when?** | Maintenance records, AI recommendations, policy automation, schedule optimization |
| **What should leadership decide?** | Executive AI reports, cost optimization, replacement planning, department benchmarks |

### End-to-end capability map

```mermaid
flowchart TB
    subgraph users [Users]
        Admin[Admin - Org wide]
        Manager[Manager - Department]
        Viewer[Viewer - Read only]
    end

    subgraph ui [React Operations Console]
        Ops[Operations Center]
        Assets[Assets and Lifecycle]
        Maint[Maintenance Center]
        Reports[Reports and Analytics]
        Asst[AI Assistant]
    end

    subgraph api [FastAPI Backend]
        RBAC[JWT and RBAC]
        Scope[Department Scoping]
        Services[Business Services]
    end

    subgraph intelligence [Intelligence Layer]
        ML[FT-Transformer Model]
        Pipeline[Autonomous Pipeline]
        Ollama[Ollama LLM optional]
    end

    subgraph data [Data Layer]
        PG[(PostgreSQL)]
        Artifacts[ml/artifacts]
    end

    Admin --> ui
    Manager --> ui
    Viewer --> ui
    ui --> api
    api --> Services
    Services --> PG
    Services --> ML
    Pipeline --> ML
    Pipeline --> PG
    Reports --> Ollama
    Asst --> Ollama
    ML --> Artifacts
```

---

## Problem Statement & Solution

**Problem:** Traditional asset management tools store records but do not *interpret* them. Operations teams see spreadsheets; leadership sees lagging indicators; maintenance is reactive; and cross-department visibility creates both data silos and privacy concerns.

**Solution:** AssetFlow AI combines:

1. **Operational truth** — PostgreSQL-backed lifecycle records every stakeholder can trust  
2. **Predictive intelligence** — ML scores every asset's health and risk continuously  
3. **Autonomous monitoring** — Drift detection and notifications surface degradation before failure  
4. **Grounded AI** — Assistant and reports cite real data; Ollama polishes language without inventing facts  
5. **Enterprise governance** — RBAC ensures viewers, managers, and admins see exactly what their role permits  

---

## Key Features by Module

### Operations Center (`/dashboard`)

The command center for daily fleet operations.

| Feature | Description |
|---------|-------------|
| **Attention Queue** | Assets needing immediate action (maintenance due, in maintenance, high risk) |
| **Live Activity Feed** | Recent allocations, transfers, maintenance, health events |
| **Compact Metrics** | Active assets, employees, maintenance due counts |
| **My Workspace** | Personal view: assigned assets, upcoming maintenance, notifications |
| **AI Recommendations** | Plain-language maintenance priorities from the FT-Transformer model |
| **Run AI Scoring** | Triggers the full intelligence pipeline (Admin/Manager) |
| **Pipeline Status** | Last run time, assets scored, scheduler state |
| **Analytics Charts** | Status distribution, department distribution |

### Assets (`/assets`, `/assets/:id`)

Full asset lifecycle management.

| Feature | Description |
|---------|-------------|
| **Asset Registry** | Search, filter, paginate, CRUD with categories and types |
| **Assign / Return / Reassign** | Employee allocation workflows with history |
| **Transfer** | Move assets between departments and locations |
| **Maintenance Records** | Preventive, corrective, inspection per asset |
| **Health Snapshots** | Manual health history entries |
| **Unified Timeline** | Chronological feed of all lifecycle events |
| **QR Scanner** | Quick asset lookup by tag |
| **AI Assessment** | Per-asset health prediction and root-cause narrative |
| **Health Trend Chart** | Historical health score visualization |

### Maintenance Center (`/maintenance`)

Fleet-wide view of assets in `IN_MAINTENANCE` status with links to detail records.

### Organization (`/departments`, `/employees`)

| Feature | Description |
|---------|-------------|
| **Departments** | CRUD for organizational units (Admin) |
| **Employees** | CRUD, department filter, allocation history |
| **User Administration** | Create accounts, reset passwords, change roles (Admin, on Employees page) |

### Reports & Analytics (`/reports`)

Enterprise analytics dashboard — see [Reports section](#reports--executive-analytics) below.

### AI Assistant (header panel)

Natural-language queries routed to grounded backend tools:

- *Which assets require maintenance?*
- *Show high-risk assets*
- *What transferred recently?*
- *How many laptops do we have?*

Optional Ollama layer formats answers; template narratives work without LLM.

### Authentication (`/login`, `/change-password`, `/settings`)

- JWT bearer authentication  
- Forced password change on first login  
- Unique temporary passwords per seeded user  
- Account settings and password management  

---

## User Roles & Access Model

Three roles are defined in [`app/core/enums.py`](app/core/enums.py) and enforced on both frontend and backend.

```mermaid
flowchart LR
    subgraph roles [Roles]
        A[ADMIN]
        M[MANAGER]
        V[VIEWER]
    end

    subgraph scope [Data Scope]
        OrgWide[Organization wide all departments]
        DeptOnly[Single department only]
    end

    subgraph actions [Write Access]
        FullWrite[All API writes]
        OpsWrite[Assets and maintenance writes]
        ReadOnly[GET and notifications only]
    end

    A --> OrgWide
    A --> FullWrite
    M --> DeptOnly
    M --> OpsWrite
    V --> DeptOnly
    V --> ReadOnly
```

| Role | Data scope | Navigation | Write access | AI pipeline | Reports |
|------|------------|------------|--------------|-------------|---------|
| **ADMIN** | All departments | All modules | Everything including users, departments, employees | Run + toggle AI Enhanced | Organization-wide report |
| **MANAGER** | Own department | All except user admin | Assets, maintenance, allocations, transfers | Run + toggle AI Enhanced | Department report + org benchmarks |
| **VIEWER** | Own department | All read modules | Read-only; mark notifications read | Passive AI narratives only | Department report + org benchmarks |

### Seeded administrator

During demo seed, the **first IT department Manager** is promoted to `ADMIN` ([`app/seeding/users.py`](app/seeding/users.py)). In a typical demo database this is:

- **Hannah Vargas** — `hannah.vargas34@assetflow.app` — Information Technology — role `ADMIN`

All other employees receive `MANAGER` (if job title is Manager) or `VIEWER` (default).

### Department scoping implementation

[`app/core/access_scope.py`](app/core/access_scope.py) provides `AccessContext`:

- `Admin.is_org_wide` → `True`; `scoping_department_id()` → `None`  
- Manager/Viewer → filtered to `employee.department_id` on assets, dashboard, operations, reports  

Frontend permissions mirror backend in [`frontend/src/features/auth/permissions.ts`](frontend/src/features/auth/permissions.ts).

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API** | FastAPI 0.115+ | Async REST API, OpenAPI docs, dependency injection |
| **ORM** | SQLAlchemy 2.x | PostgreSQL access, relationship mapping |
| **Migrations** | Alembic | Versioned schema evolution |
| **Validation** | Pydantic v2 | Request/response schemas, settings |
| **Database** | PostgreSQL 14+ | Operational source of truth |
| **Frontend** | React 18 + TypeScript | SPA operations console |
| **Build** | Vite 5 | Dev server, production bundling |
| **State** | TanStack Query | Server state, caching, mutations |
| **Styling** | Tailwind CSS | Utility-first responsive UI |
| **Charts** | Recharts | Reports and dashboard visualizations |
| **ML** | PyTorch FT-Transformer | Tabular health prediction |
| **LLM** | Ollama (optional) | Narrative enhancement for reports and assistant |
| **Auth** | PyJWT + bcrypt | Token issuance and password hashing |
| **HTTP client** | httpx | Ollama API calls |
| **Testing** | pytest + TestClient | Unit and integration tests |

---

## System Architecture

### Layered backend

Every API request follows strict layering:

```mermaid
flowchart TB
    Client[React Client]
    Router[API Router app/api/v1/endpoints]
    Auth[auth_deps: JWT + RBAC + AccessContext]
    Service[Service Layer app/services]
    Repo[Repository Layer app/repositories]
    Model[SQLAlchemy Models app/models]
    DB[(PostgreSQL)]

    Client -->|HTTP| Router
    Router --> Auth
    Auth --> Service
    Service --> Repo
    Repo --> Model
    Model --> DB
```

| Layer | Responsibility | Example |
|-------|----------------|---------|
| **Endpoints** | HTTP routing, query params, status codes | `operations.py`, `assets.py` |
| **Services** | Business rules, orchestration, AI logic | `reports_analytics_service.py` |
| **Repositories** | SQL queries, pagination, filters | `asset_repository.py` |
| **Models** | Table definitions, relationships | `asset.py`, `user.py` |
| **Schemas** | API contracts (Pydantic) | `reports_analytics.py` |

### Application entry points

| Component | Path |
|-----------|------|
| Backend startup | [`app/main.py`](app/main.py) |
| API router aggregation | [`app/api/v1/router.py`](app/api/v1/router.py) |
| Dependency injection | [`app/api/deps.py`](app/api/deps.py) |
| Auth middleware | [`app/api/auth_deps.py`](app/api/auth_deps.py) |
| Frontend bootstrap | [`frontend/src/main.tsx`](frontend/src/main.tsx) |
| Route definitions | [`frontend/src/app/router/routes.tsx`](frontend/src/app/router/routes.tsx) |

### Cross-cutting concerns

| Concern | Implementation |
|---------|----------------|
| **Request logging** | [`app/middleware/request_logging.py`](app/middleware/request_logging.py) |
| **Exception handling** | [`app/exceptions/handlers.py`](app/exceptions/handlers.py) |
| **Health checks** | `GET /health`, `GET /ready` ([`app/core/health_checks.py`](app/core/health_checks.py)) |
| **Background scheduler** | [`app/services/scheduler_service.py`](app/services/scheduler_service.py) (optional) |
| **CORS** | Configured in [`app/main.py`](app/main.py) for localhost dev ports |

---

## Data Flow Diagrams

### Asset lifecycle

```mermaid
stateDiagram-v2
    [*] --> AVAILABLE: Register asset
    AVAILABLE --> ASSIGNED: Assign to employee
    ASSIGNED --> AVAILABLE: Return
    ASSIGNED --> ASSIGNED: Reassign
    AVAILABLE --> IN_MAINTENANCE: Schedule maintenance
    ASSIGNED --> IN_MAINTENANCE: Schedule maintenance
    IN_MAINTENANCE --> AVAILABLE: Complete maintenance
    IN_MAINTENANCE --> ASSIGNED: Complete maintenance
    AVAILABLE --> RETIRED: Retire
    ASSIGNED --> RETIRED: Retire
    RETIRED --> DISPOSED: Dispose
    DISPOSED --> [*]
```

Each transition creates records in `asset_allocations`, `asset_transfers`, `maintenance_records`, or `asset_health_history`, and appears on the asset **Timeline**.

### Intelligence pipeline

Triggered by **Run AI Scoring** or the background scheduler:

```mermaid
sequenceDiagram
    participant UI as Dashboard or Reports
    participant API as POST /operations/pipeline/run
    participant Pipe as IntelligencePipelineService
    participant ML as PredictionService FT-Transformer
    participant Drift as DriftMonitoringService
    participant Policy as PolicyAutomationService
    participant DB as PostgreSQL

    UI->>API: Run pipeline
    API->>Pipe: run_full_pipeline
    Pipe->>ML: score_batch all assets
    ML->>DB: Persist health history optional
    Pipe->>Drift: detect_drift
    Pipe->>Policy: run_policies
    Policy->>DB: Auto-schedule maintenance
    Policy->>DB: Create notifications
    Pipe-->>UI: scored drift_alerts notifications_created
    UI->>UI: Refresh KPIs recommendations reports
```

### Reports analytics (staged loading)

```mermaid
sequenceDiagram
    participant UI as Reports Page
    participant API as GET /operations/reports/analytics
    participant Svc as ReportsAnalyticsService
    participant Ollama as Ollama optional

    UI->>API: use_ai=false
    API->>Svc: build template analytics
    Svc-->>UI: KPIs charts executive sections fast

    UI->>API: use_ai=true
    API->>Svc: build with LLM enhancement
    par Parallel Ollama calls
        Svc->>Ollama: Executive sections JSON
        Svc->>Ollama: Drift insight
        Svc->>Ollama: Cost insight
        Svc->>Ollama: Replacement insight
        Svc->>Ollama: Maintenance insight
    end
    Svc-->>UI: Enhanced narratives source=ollama
```

### AI Assistant request flow

```mermaid
flowchart LR
    User[User message] --> Parse[assistant_parsing intent detection]
    Parse --> Tools[assistant_tools grounded queries]
    Tools --> DB[(PostgreSQL + prediction cache)]
    Tools --> Facts[Structured tool result]
    Facts --> Ollama{Ollama enabled?}
    Ollama -->|Yes| Format[LLM format with validation]
    Ollama -->|No| Template[narrative.py templates]
    Format --> Response[AssistantChatResponse]
    Template --> Response
```

---

## AI & Machine Learning Pipeline

### Dual-dataset architecture

| Dataset | Source | Purpose |
|---------|--------|---------|
| **Operational (PostgreSQL)** | `py -m app.seeding --profile demo` | Application demo ~200 assets, 18 months history |
| **Training (Parquet files)** | `py -m ml.data --rows 80000` | FT-Transformer training; never loaded into PostgreSQL |

See [`ml/README.md`](ml/README.md) for training commands.

### FT-Transformer health model

| Output | Description |
|--------|-------------|
| `health_score` | 0.0–1.0 predicted fleet health |
| `risk_level` | LOW / MEDIUM / HIGH derived from score thresholds |
| `confidence` | Model confidence for the prediction |
| `explanation` | Feature-level factors (utilization, maintenance overdue, etc.) |
| `features_used` | Input feature names from [`app/services/feature_engineering.py`](app/services/feature_engineering.py) |

**Key services:**

| Service | File | Role |
|---------|------|------|
| Prediction | [`prediction_service.py`](app/services/prediction_service.py) | Inference, batch scoring, cache |
| Feature engineering | [`feature_engineering.py`](app/services/feature_engineering.py) | Asset → model input vector |
| Explanation | [`prediction_explanation_service.py`](app/services/prediction_explanation_service.py) | Human-readable factor breakdown |
| Recommendations | [`recommendation_service.py`](app/services/recommendation_service.py) | Maintenance priority list |
| Root cause | [`root_cause_service.py`](app/services/root_cause_service.py) | Asset-level AI assessment narrative |
| Drift | [`drift_monitoring_service.py`](app/services/drift_monitoring_service.py) | Score change detection |
| Policy automation | [`policy_automation_service.py`](app/services/policy_automation_service.py) | Rule-based maintenance + notifications |
| Pipeline | [`intelligence_pipeline_service.py`](app/services/intelligence_pipeline_service.py) | Orchestrates full scoring run |

### Ollama integration

Used when `ASSISTANT_USE_OLLAMA=true`:

| Consumer | Behavior |
|----------|----------|
| **AI Assistant** | Formats grounded tool results; validates output against facts |
| **Reports analytics** | Enhances executive sections and section insights |
| **Weekly report** | Optional LLM brief via `use_llm=true` |
| **Root cause** | Optional LLM narrative on asset detail |

Client: [`app/services/ollama_client.py`](app/services/ollama_client.py)

---

## Reports & Executive Analytics

The Reports module (`/reports`) is a unified **AI-powered analytics platform** backed by `GET /operations/reports/analytics`.

### Executive AI Report — 11 sections

| # | Section | Content |
|---|---------|---------|
| 1 | Executive Summary | Fleet overview for leadership |
| 2 | Overall Fleet Health | AI-scored health and risk breakdown |
| 3 | Major Events This Week | Maintenance, drift, lifecycle signals |
| 4 | Assets Requiring Immediate Attention | High-risk asset list |
| 5 | Maintenance Performance | Overdue work and schedule coverage |
| 6 | Department-wise Performance | Relative health by department |
| 7 | AI Observations | Model-driven patterns |
| 8 | Risk Analysis | FT-Transformer risk classification |
| 9 | Predicted Issues | Failure risk if maintenance skipped |
| 10 | Recommended Actions | Prioritized operational and financial actions |
| 11 | Expected Impact Next Week | Projected outcomes if actions taken |

### Operational analytics sections

| Section | Visualizations | AI content |
|---------|----------------|------------|
| **Health Drift** | Health change bar chart, dept comparison | Interpretation, key factors, improving vs deteriorating counts |
| **Cost Optimization** | TCO distribution, department spend charts | Savings estimate, opportunities list |
| **Replacement Planning** | Enriched asset cards | Why replace, remaining life, repair vs replace, delay impact |
| **Maintenance Schedule** | Priority ranking, dept workload charts | Skip-risk summary, optimization suggestions |

### Role-specific Reports UX

| User | Report title | Benchmark KPIs | AI controls |
|------|--------------|----------------|-------------|
| **Admin** | Organization-wide report | Hidden (full org data shown elsewhere) | AI Enhanced toggle + Run AI Scoring |
| **Manager** | `{Department} department report` | Company avg health, dept vs company, company high-risk count | AI Enhanced toggle + Run AI Scoring |
| **Viewer** | `{Department} department report` | Same benchmarks | Passive AI narratives; no scoring button |

---

## Database & Domain Model

### Core entities

```mermaid
erDiagram
    DEPARTMENTS ||--o{ EMPLOYEES : employs
    EMPLOYEES ||--o| USERS : authenticates
    DEPARTMENTS ||--o{ ASSETS : owns
    EMPLOYEES ||--o{ ASSETS : assigned
    ASSETS ||--o{ ASSET_ALLOCATIONS : history
    ASSETS ||--o{ ASSET_TRANSFERS : history
    ASSETS ||--o{ MAINTENANCE_RECORDS : has
    ASSETS ||--o{ ASSET_HEALTH_HISTORY : tracks
    ASSETS }o--|| ASSET_TYPES : typed
    ASSET_TYPES }o--|| ASSET_CATEGORIES : categorized
    ASSETS ||--o{ NOTIFICATIONS : triggers

    DEPARTMENTS {
        uuid id PK
        string code
        string name
    }
    EMPLOYEES {
        uuid id PK
        uuid department_id FK
        string email
        string job_title
    }
    USERS {
        uuid id PK
        uuid employee_id FK
        enum role
        bool must_change_password
    }
    ASSETS {
        uuid id PK
        string asset_tag
        uuid current_department_id FK
        enum current_status
    }
```

### Alembic migrations

| Migration | Purpose |
|-----------|---------|
| `001_initial_schema.py` | Core tables: departments, employees, assets, lifecycle |
| `002_notifications.py` | Notification system |
| `003_notification_types.py` | Typed notification enums |
| `004_users.py` | User authentication table |
| `005_user_employee_link.py` | Employee ↔ user relationship |
| `006_user_password_flags.py` | `must_change_password` flag |

Reference SQL (not migration source of truth): [`docs/database/reference_schema.sql`](docs/database/reference_schema.sql)

---

## Complete Project Structure

```
AssetFlow-AI/
│
├── app/                                    # ── BACKEND (FastAPI) ──
│   ├── main.py                             # App entry, CORS, lifespan, /health, /ready
│   ├── api/
│   │   ├── deps.py                         # Service dependency injection factory
│   │   ├── auth_deps.py                    # JWT, RBAC enforcement, AccessContext
│   │   └── v1/
│   │       ├── router.py                   # Route aggregation (public + protected)
│   │       └── endpoints/
│   │           ├── auth.py                 # Login, me, change-password, user admin
│   │           ├── departments.py          # Department CRUD
│   │           ├── employees.py            # Employee CRUD
│   │           ├── lookups.py              # Asset categories and types
│   │           ├── assets.py               # Asset CRUD and search
│   │           ├── allocations.py          # Assign, return, reassign
│   │           ├── transfers.py            # Inter-department transfers
│   │           ├── maintenance.py          # Maintenance records
│   │           ├── health_history.py       # Manual health snapshots
│   │           ├── timeline.py             # Unified asset timeline
│   │           ├── dashboard.py            # Summary + my-workspace
│   │           ├── intelligence.py         # ML scoring, recommendations, root cause
│   │           ├── assistant.py            # AI chat endpoint
│   │           └── operations.py           # Pipeline, notifications, reports, drift, cost
│   ├── core/
│   │   ├── config.py                       # Settings from .env (Pydantic)
│   │   ├── database.py                     # SQLAlchemy engine and session
│   │   ├── enums.py                        # Status enums, UserRole
│   │   ├── security.py                     # JWT and bcrypt
│   │   ├── permissions.py                  # API-level RBAC matrix
│   │   ├── access_scope.py                 # Department scoping context
│   │   ├── password_policy.py              # Temp password generation and validation
│   │   ├── health_checks.py                # /ready DB and ML checks
│   │   ├── health_thresholds.py            # Risk band thresholds
│   │   └── json_sanitize.py                # JSON serialization helpers
│   ├── models/                             # SQLAlchemy ORM models
│   │   ├── department.py, employee.py, user.py
│   │   ├── asset.py, allocation.py, transfer.py
│   │   ├── maintenance.py, health_history.py
│   │   └── notification.py
│   ├── repositories/                       # Data access layer
│   │   ├── asset_repository.py, employee_repository.py
│   │   ├── department_repository.py, maintenance_repository.py
│   │   ├── dashboard_repository.py, timeline_repository.py
│   │   ├── health_history_repository.py, notification_repository.py
│   │   └── user_repository.py
│   ├── schemas/                            # Pydantic API contracts
│   │   ├── auth.py, dashboard.py, operations.py
│   │   ├── intelligence.py, explanation.py, recommendation.py
│   │   ├── reports_analytics.py            # Reports page response models
│   │   └── workspace.py                    # My Workspace DTOs
│   ├── services/                           # Business logic
│   │   ├── auth_service.py                 # Login, user CRUD
│   │   ├── asset_service.py                # Asset operations
│   │   ├── allocation_service.py           # Assign/return/reassign
│   │   ├── transfer_service.py             # Department transfers
│   │   ├── maintenance_service.py          # Maintenance CRUD
│   │   ├── health_history_service.py       # Health snapshots
│   │   ├── timeline_service.py             # Event aggregation
│   │   ├── department_service.py           # Department CRUD
│   │   ├── employee_service.py             # Employee CRUD
│   │   ├── dashboard_service.py            # Operations summary
│   │   ├── workspace_service.py            # My Workspace
│   │   ├── prediction_service.py           # FT-Transformer inference
│   │   ├── feature_engineering.py          # ML feature vectors
│   │   ├── prediction_explanation_service.py
│   │   ├── recommendation_service.py       # Maintenance recommendations
│   │   ├── root_cause_service.py           # Asset AI assessment
│   │   ├── drift_monitoring_service.py       # Health drift detection
│   │   ├── cost_optimization_service.py    # TCO analysis
│   │   ├── replacement_planning_service.py # Lifecycle refresh planning
│   │   ├── maintenance_scheduling_service.py
│   │   ├── report_service.py               # Weekly operations brief
│   │   ├── reports_analytics_service.py      # Unified Reports page builder
│   │   ├── intelligence_pipeline_service.py
│   │   ├── policy_automation_service.py    # Auto-maintenance rules
│   │   ├── notification_service.py         # Alert management
│   │   ├── knowledge_graph_service.py      # Asset graph API
│   │   ├── scheduler_service.py            # Background pipeline scheduler
│   │   ├── assistant_service.py            # Chat orchestration
│   │   ├── assistant_tools.py              # Grounded query tools
│   │   ├── assistant_parsing.py            # Intent detection
│   │   ├── assistant_intents.py            # Intent definitions
│   │   ├── narrative.py                      # Template text generators
│   │   ├── ollama_client.py                  # Ollama HTTP client
│   │   └── priority_scoring.py               # Recommendation ranking
│   ├── seeding/                            # Demo data generation
│   │   ├── generator.py                    # Assets, history, employees
│   │   ├── users.py                        # Login account creation
│   │   ├── profiles.py                     # minimal / demo / ml profiles
│   │   ├── manifest.py                     # Fixed demo asset tags
│   │   └── reset.py                        # Operational data reset
│   ├── middleware/
│   │   └── request_logging.py
│   └── exceptions/
│       ├── errors.py
│       └── handlers.py
│
├── frontend/                               # ── FRONTEND (React + TypeScript) ──
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── main.tsx                        # React bootstrap
│       ├── app/
│       │   ├── router/
│       │   │   ├── routes.tsx              # All route definitions
│       │   │   ├── protected-route.tsx       # Auth gate
│       │   │   └── role-route.tsx          # Permission gate
│       │   ├── layout/
│       │   │   ├── app-shell.tsx           # Sidebar + header shell
│       │   │   ├── sidebar.tsx             # Role-filtered navigation
│       │   │   ├── header.tsx              # Search, notifications, assistant
│       │   │   └── breadcrumbs.tsx
│       │   └── providers/
│       │       └── query-provider.tsx      # TanStack Query setup
│       ├── pages/                            # Thin route wrappers
│       │   ├── login-page.tsx
│       │   ├── change-password-page.tsx
│       │   ├── dashboard-page.tsx
│       │   ├── assets-page.tsx
│       │   ├── asset-detail-page.tsx
│       │   ├── maintenance-page.tsx
│       │   ├── departments-page.tsx
│       │   ├── employees-page.tsx
│       │   ├── reports-page.tsx
│       │   └── settings-page.tsx
│       ├── features/                         # Domain modules
│       │   ├── auth/
│       │   │   ├── auth-context.tsx          # Session state
│       │   │   ├── permissions.ts            # Role → permission map
│       │   │   ├── use-permissions.ts
│       │   │   ├── api.ts                    # Login, me, users
│       │   │   └── types.ts
│       │   ├── dashboard/
│       │   │   ├── components/               # Operations Center UI
│       │   │   │   ├── attention-queue.tsx
│       │   │   │   ├── activity-feed.tsx
│       │   │   │   ├── compact-metrics-strip.tsx
│       │   │   │   ├── my-workspace-panel.tsx
│       │   │   │   ├── analytics-section.tsx
│       │   │   │   ├── quick-actions-panel.tsx
│       │   │   │   └── ...
│       │   │   ├── hooks/use-dashboard-summary.ts
│       │   │   └── api/dashboard-api.ts
│       │   ├── assets/
│       │   │   ├── components/               # Registry, detail, lifecycle, QR
│       │   │   ├── hooks/                    # use-assets, use-lifecycle
│       │   │   └── api/                      # assets-api, lifecycle-api
│       │   ├── maintenance/
│       │   ├── departments/
│       │   ├── employees/
│       │   ├── reports/
│       │   │   ├── components/
│       │   │   │   ├── reports-page-content.tsx  # Main Reports UI
│       │   │   │   └── report-bar-chart.tsx      # Recharts wrapper
│       │   ├── intelligence/
│       │   │   ├── components/ai-recommendations-panel.tsx
│       │   │   ├── hooks/use-intelligence.ts
│       │   │   └── api/intelligence-api.ts
│       │   ├── operations/
│       │   │   ├── components/               # Notifications bell/panel, pipeline strip
│       │   │   ├── hooks/use-operations.ts   # Reports, pipeline, notifications hooks
│       │   │   └── api/operations-api.ts
│       │   └── assistant/
│       │       └── components/assistant-panel.tsx
│       ├── shared/
│       │   ├── api/client.ts                 # Fetch wrapper, JWT, timeouts
│       │   ├── components/ui/                # Button, Card, Dialog, Table, ...
│       │   ├── components/data-display/      # Tables, badges, pagination
│       │   ├── components/feedback/          # Toast, empty state, confirm
│       │   └── lib/                          # utils, date, format, ops-semantics
│       └── styles/
│           ├── globals.css
│           └── ops-dashboard.css
│
├── ml/                                     # ── MACHINE LEARNING ──
│   ├── README.md
│   ├── config.py
│   ├── train.py                            # FT-Transformer training
│   ├── predict.py                          # CLI inference test
│   ├── data/                               # Synthetic training data generator
│   ├── etl/                                # Parquet → normalized dataset
│   ├── models/                             # PyTorch model definition
│   └── artifacts/                          # model.pt, feature_stats.json (gitignored)
│
├── alembic/                                # Database migrations
│   └── versions/                           # 001–006 migration chain
│
├── tests/                                  # pytest suite
│   ├── conftest.py
│   ├── test_access_scope.py
│   ├── test_permissions.py
│   ├── test_password_policy.py
│   ├── test_reports_analytics_benchmarks.py
│   ├── test_auth_integration.py
│   └── test_health.py
│
├── scripts/dev/                            # Manual dev/diagnostic scripts
│   ├── README.md
│   ├── test_routing.py                     # Assistant routing regression
│   └── test_auth_rbac.py                   # Auth manual integration script
│
├── docs/
│   ├── DEMO.md                             # 5-minute demo script
│   ├── FRONTEND_ARCHITECTURE.md            # UI architecture blueprint
│   └── database/reference_schema.sql       # Reference SQL schema
│
├── requirements.txt                        # Python production dependencies
├── requirements-dev.txt                    # pytest and dev tools
├── requirements-ml.txt                     # PyTorch and ML dependencies
├── pytest.ini
├── alembic.ini
├── .env.example
└── README.md                               # This file
```

---

## Getting Started

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 14+ |
| Ollama (optional) | Latest + `llama3.2:3b` |

### Installation

```bash
# Backend dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Frontend dependencies
cd frontend && npm install && cd ..
```

### Environment setup

```bash
cp .env.example .env
```

Edit `.env` — minimum required:

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/assetflow_ai
JWT_SECRET_KEY=your-long-random-secret
ASSISTANT_USE_OLLAMA=true
```

### Database initialization

```bash
py -m alembic upgrade head
py -m app.seeding --profile demo --reset
```

The seed command prints sample login credentials. **Change password on first login.**

| Profile | Assets | History | Use case |
|---------|--------|---------|----------|
| `minimal` | 30 | 30 days | Quick dev / CI |
| `demo` | 200 + 20 inactive | 18 months | Default evaluation |
| `ml` | 200 | 18 months + dense health | ML training prep |

### Run the application

```powershell
# Terminal 1 — Backend
$env:PYTHONPATH='.'; py -m uvicorn app.main:app --port 8000 --reload

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open **http://localhost:5173** and sign in with seeded credentials.

### Verify services

| Endpoint | Expected |
|----------|----------|
| http://127.0.0.1:8000/health | `{"status":"ok"}` |
| http://127.0.0.1:8000/ready | DB + ML model checks |
| http://127.0.0.1:8000/docs | Swagger UI |

### Optional: Ollama for AI narratives

```powershell
ollama pull llama3.2:3b
```

Ensure `ASSISTANT_USE_OLLAMA=true` in `.env`.

### Windows troubleshooting

| Issue | Fix |
|-------|-----|
| Port 8000 in use | `netstat -ano \| findstr :8000` then `taskkill /PID <pid> /F` |
| Port 5173 in use | Stop other Node processes or change Vite port |
| OneDrive file locks | Vite cache uses `%TEMP%\vite-cache-assetflow` |

---

## Configuration Reference

Full template: [`.env.example`](.env.example)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | PostgreSQL connection string |
| `APP_NAME` | AssetFlow AI | Display name |
| `DEBUG` | false | Verbose logging |
| `AUTH_ENABLED` | true | JWT authentication |
| `JWT_SECRET_KEY` | — | Token signing secret |
| `JWT_EXPIRE_MINUTES` | 480 | Session lifetime |
| `ML_ENABLED` | true | Enable FT-Transformer inference |
| `ML_MODEL_PATH` | ml/artifacts/model.pt | Model weights path |
| `ASSISTANT_USE_OLLAMA` | true | LLM narrative enhancement |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama server |
| `OLLAMA_MODEL` | llama3.2:3b | Model tag |
| `OLLAMA_TIMEOUT_SECONDS` | 30 | LLM request timeout |
| `SCHEDULER_ENABLED` | false | Background pipeline |
| `SCHEDULER_INTERVAL_MINUTES` | 60 | Pipeline interval |
| `POLICY_AUTOMATION_ENABLED` | true | Auto-maintenance rules |
| `DRIFT_MIN_DROP` | 0.10 | Drift alert threshold |

---

## API Reference

Base URL: `http://127.0.0.1:8000/api/v1`

Interactive docs: **http://127.0.0.1:8000/docs**

### Authentication

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | Public | Obtain JWT access token |
| GET | `/auth/me` | Bearer | Current user profile |
| POST | `/auth/change-password` | Bearer | Update password |
| GET | `/auth/users` | Admin | List all users |
| POST | `/auth/users` | Admin | Create user account |
| PATCH | `/auth/users/{id}` | Admin | Update role / active status |
| POST | `/auth/users/{id}/reset-password` | Admin | Reset to temp password |

### Organization

| Method | Path | Description |
|--------|------|-------------|
| CRUD | `/departments` | Department management |
| CRUD | `/employees` | Employee management |
| GET | `/asset-categories`, `/asset-types` | Lookup data |

### Asset lifecycle

| Method | Path | Description |
|--------|------|-------------|
| CRUD | `/assets` | Asset registry |
| GET | `/assets/search` | Full-text search |
| POST | `/assets/{id}/allocations/assign` | Assign to employee |
| POST | `/assets/{id}/allocations/return` | Return asset |
| POST | `/assets/{id}/allocations/reassign` | Reassign |
| POST | `/assets/{id}/transfers` | Department transfer |
| CRUD | `/assets/{id}/maintenance` | Maintenance records |
| CRUD | `/assets/{id}/health-history` | Health snapshots |
| GET | `/assets/{id}/timeline` | Unified event timeline |

### Dashboard & workspace

| Method | Path | Description |
|--------|------|-------------|
| GET | `/dashboard/summary` | Operations Center metrics |
| GET | `/dashboard/my-workspace` | Personal assigned assets and alerts |

### Intelligence & AI

| Method | Path | Description |
|--------|------|-------------|
| POST | `/intelligence/score-batch` | Batch FT-Transformer scoring |
| POST | `/intelligence/assets/{id}/predict` | Single asset prediction |
| GET | `/intelligence/high-risk` | High-risk asset list |
| GET | `/intelligence/recommendations` | Maintenance recommendations |
| GET | `/intelligence/assets/{id}/root-cause` | Root cause analysis |
| POST | `/assistant/chat` | AI assistant chat |

### Operations & reports

| Method | Path | Description |
|--------|------|-------------|
| GET | `/operations/pipeline/status` | Pipeline state |
| POST | `/operations/pipeline/run` | Run full AI pipeline |
| GET | `/operations/notifications` | Department-scoped alerts |
| PATCH | `/operations/notifications/{id}/read` | Mark read |
| GET | `/operations/drift` | Health drift status |
| GET | `/operations/reports/analytics` | Unified Reports page data |
| GET | `/operations/reports/weekly` | Weekly operations brief |
| GET | `/operations/replacement-plan` | Replacement candidates |
| GET | `/operations/cost-optimization` | Cost analysis |
| GET | `/operations/maintenance-schedule` | Schedule suggestions |
| GET | `/operations/graph/assets/{id}` | Knowledge graph neighborhood |

---

## Testing & Quality Assurance

```bash
# Unit tests (no live DB required for most)
py -m pytest tests/ -m "not integration" -q

# Integration tests (requires PostgreSQL with seed data)
py -m pytest tests/ -m integration -q

# Assistant routing regression
$env:PYTHONPATH='.'; py scripts/dev/test_routing.py

# Frontend production build
cd frontend && npm run build
```

| Test file | What it verifies |
|-----------|------------------|
| `test_access_scope.py` | Admin org-wide vs department scoping |
| `test_permissions.py` | API write permission matrix |
| `test_password_policy.py` | Password generation rules |
| `test_reports_analytics_benchmarks.py` | Org benchmark KPIs for non-admins |
| `test_auth_integration.py` | Login, password change, RBAC flows |
| `test_health.py` | Liveness endpoint |

---

## Demo & Evaluation

See **[docs/DEMO.md](docs/DEMO.md)** for the full 5-minute walkthrough.

**Fixed demo asset tags** (from [`app/seeding/manifest.py`](app/seeding/manifest.py)):

| Tag | Type | Purpose |
|-----|------|---------|
| `IT-LAP-0001` | Laptop | Primary lifecycle demo |
| `OPS-VAN-001` | Delivery Van | Fleet operations |
| `SRV-PROD-01` | Server | Infrastructure |
| `ADM-PRT-001` | Printer | Office equipment + AI assessment |

**Suggested evaluation flow:**

1. Login as Admin (Hannah Vargas) → verify org-wide dashboard  
2. Run AI Scoring → observe recommendations and notifications  
3. Open Reports → toggle AI Enhanced → review executive sections  
4. Login as department Viewer → verify scoped data and benchmark KPIs  
5. Use AI Assistant with fleet queries  
6. Walk through asset lifecycle on `IT-LAP-0001`  

---

## Roadmap & Future Enhancements

Planned improvements identified during development and evaluation:

### Reports & analytics

- [ ] Dedicated **Asset Health Reports** and **Department Reports** sub-pages
- [ ] **Post-scoring diff panel** — highlight assets whose scores changed after pipeline runs
- [ ] **Risk heatmaps** and interactive health trend timelines
- [ ] **Prediction confidence** and risk-trend-over-time in Health Drift
- [ ] **SHAP-style key contributing factors** per asset in reports
- [ ] Richer **repair vs replace lifecycle cost modeling**
- [ ] **PDF/Excel export** for executive reports

### AI & platform

- [ ] Optional **Executive Viewer** role (org-wide read-only without Admin write access)
- [ ] Stronger Ollama JSON reliability for all 11 executive sections in one pass
- [ ] **Docker Compose** one-command deployment profile
- [ ] **SSE/WebSocket** live updates when pipeline completes
- [ ] **"Last AI Scored: X min ago"** persistent badge across all modules

### Enterprise hardening

- [ ] **Audit log** for admin actions and pipeline runs
- [ ] **SSO / OIDC** integration
- [ ] **Rate limiting** and API keys for external integrations
- [ ] **Multi-tenant** organization support

---

## Additional Documentation

| Document | Description |
|----------|-------------|
| [docs/DEMO.md](docs/DEMO.md) | Step-by-step 5-minute demo script |
| [docs/FRONTEND_ARCHITECTURE.md](docs/FRONTEND_ARCHITECTURE.md) | Frontend product architecture blueprint |
| [docs/database/reference_schema.sql](docs/database/reference_schema.sql) | Reference SQL schema |
| [ml/README.md](ml/README.md) | ML training pipeline and artifacts |
| [scripts/dev/README.md](scripts/dev/README.md) | Dev/diagnostic script index |

---

## License & Attribution

Academic and enterprise evaluation project — **AssetFlow AI Intelligent Asset Lifecycle Management System**.
