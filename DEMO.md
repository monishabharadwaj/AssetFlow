# AssetFlow AI — 5-Minute Demo Script

## Prerequisites

1. Run migrations: `py -m alembic upgrade head`
2. Seed demo data: `py -m app.seeding --profile demo --reset`
3. Backend: `py -m uvicorn app.main:app --reload` (port 8000)
4. Frontend: `cd frontend && npm run dev` (port 5173)
5. **(Optional)** Ollama for richer assistant phrasing:
   ```powershell
   ollama pull llama3.2:3b
   ```
   Set in `.env`: `ASSISTANT_USE_OLLAMA=true`, `OLLAMA_MODEL=llama3.2:3b`  
   Without Ollama, the assistant still answers using tool data + plain-English narratives.

## Seeded demo asset tags

Use these fixed tags from the demo seed profile:

| Tag | Type | Purpose |
|-----|------|---------|
| `IT-LAP-0001` | Laptop | Primary assign/transfer demo |
| `OPS-VAN-001` | Delivery Van | Fleet / operations demo |
| `SRV-PROD-01` | Server | Infrastructure asset (datacenter) |
| `ADM-PRT-001` | Printer | Office equipment demo |

## Walkthrough

### 1. Operations Center (30s)

- Open `http://localhost:5173/dashboard`
- Highlight **Attention Queue** (maintenance due, in-maintenance assets)
- Highlight **Live Activity** feed (15 recent events)
- Note compact metrics strip (assets, employees, maintenance due)

### 2. Register an Asset (1 min)

- Go to **Assets** → **Register Asset**
- Fill tag, name, category/type, department, purchase info
- Save → asset appears in table

### 3. Asset Lifecycle (2 min)

- Open `IT-LAP-0001` from search or assets table
- **Assign** to an employee
- **Transfer** to another department/location
- **Add Maintenance** record
- **Health Snapshot** with score and condition rating
- Switch to **Timeline** tab → unified chronological feed

### 4. Organization (1 min)

- **Departments** → list, create, edit
- **Employees** → list, filter by department, view allocation history

### 5. Maintenance Center (30s)

- **Maintenance** → assets in `IN_MAINTENANCE` status
- Link through to per-asset maintenance records

### 6. AI Intelligence (1 min)

- On **Operations Center**, click **Run AI scoring** (once per session)
- Review **AI Recommendations** panel (plain-language maintenance priorities)
- Open **Assistant** (header) and try:
  - *Which assets require maintenance?*
  - *Show high-risk assets*
  - *What transferred recently?*
  - *How many laptops do we have?*
- Open `ADM-PRT-001` → **Run AI Assessment** on asset detail

**API test (Swagger):** `POST /api/v1/assistant/chat` with `{"message": "Which assets require maintenance?"}`

## Talking Points

- Reproducible enterprise seed: 200 active assets, 18 months of history
- Full-stack FastAPI + PostgreSQL backend with layered architecture
- React + TanStack Query frontend with operations-first UX
- Asset-centric lifecycle with unified timeline and attention queue
- FT-Transformer health prediction (MAE ~0.035 on synthetic training set)
- Tool-based assistant with Ollama optional layer (`llama3.2:3b`) and narrative fallback
