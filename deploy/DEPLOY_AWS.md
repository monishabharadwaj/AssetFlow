# Deploy AssetFlow AI on AWS (Option A — no Docker)

All-in-one **Ubuntu EC2**: PostgreSQL + FastAPI (uvicorn/systemd) + React (`frontend/dist`) behind **nginx**.

```text
Browser → nginx :80
           ├─ /          → frontend/dist (SPA)
           ├─ /api/      → uvicorn 127.0.0.1:8000
           └─ /health|/ready|/docs → uvicorn
uvicorn → PostgreSQL (localhost) + ml/artifacts/
```

Same-origin UI: build with `VITE_API_BASE_URL=/api/v1` so the browser talks to nginx only.

---

## 1. Prerequisites

- AWS account
- EC2 key pair (`.pem`)
- Recommended instance: **`t3.small`** (2 GB). Use **`t3.medium`** if ML inference is slow or OOM
- Storage: 20–30 GB gp3
- GitHub/repo access to clone AssetFlow AI
- Locally trained ML artifacts (or train on the server):
  - `ml/artifacts/model.pt`
  - `ml/artifacts/feature_stats.json`

**Cost tip (India):** stop the EC2 when not demoing. Stopped instances still bill for EBS (~₹150–400/month). Running `t3.small` 24/7 is roughly ₹1,100–1,400/month.

---

## 2. Launch EC2

1. AMI: **Ubuntu 22.04 LTS**
2. Instance type: `t3.small` (or `t3.medium`)
3. Security group inbound:
   - **22** — SSH from your IP only
   - **80** — HTTP from `0.0.0.0/0` (demo)
   - **443** — optional later for HTTPS
4. Do **not** open port **8000** publicly — nginx is the only public entry
5. (Optional) Allocate an **Elastic IP** and associate it so the public IP stays stable across stop/start

SSH:

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

---

## 3. Install packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git nginx postgresql postgresql-contrib build-essential

# Node 20 for frontend build
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v   # expect v20.x
```

---

## 4. PostgreSQL setup

```bash
sudo -u postgres psql -c "CREATE USER assetflow WITH PASSWORD 'CHOOSE_A_STRONG_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE assetflow_ai OWNER assetflow;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE assetflow_ai TO assetflow;"
```

URL-encode special characters in the password when putting it in `DATABASE_URL` (`@` → `%40`).

---

## 5. Clone repo and Python deps

```bash
cd /home/ubuntu
git clone https://github.com/YOUR_USER/AssetFlow-AI.git
cd AssetFlow-AI

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-ml.txt
```

---

## 6. Configure `.env`

```bash
cp deploy/.env.production.example .env
nano .env
```

Replace at least:

- `CHOOSE_A_STRONG_PASSWORD` / `CHANGE_ME` in `DATABASE_URL`
- `JWT_SECRET_KEY` — generate with:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

- `CORS_ORIGINS=http://YOUR_EC2_PUBLIC_IP` (optional with same-origin UI; useful for `/docs` from the public IP)
- Confirm `ML_MODEL_PATH` and `ML_FEATURE_STATS_PATH` match your install path

Leave `ASSISTANT_USE_OLLAMA=false` for the first deploy.

---

## 7. ML artifacts

**Preferred — copy from your laptop** (after local training):

```bash
# from your laptop (PowerShell / Git Bash)
scp -i your-key.pem ml/artifacts/model.pt ml/artifacts/feature_stats.json ubuntu@YOUR_EC2_PUBLIC_IP:/home/ubuntu/AssetFlow-AI/ml/artifacts/
```

Ensure the directory exists on the server first:

```bash
mkdir -p /home/ubuntu/AssetFlow-AI/ml/artifacts
```

**Alternative — train on EC2** (slower, more RAM/disk):

```bash
cd /home/ubuntu/AssetFlow-AI
source .venv/bin/activate
python -m ml.data --rows 80000 --assets 9000 --seed 42
python -m ml.etl --source file
python -m ml.train
```

Training parquet files are **not** required for inference after `model.pt` and `feature_stats.json` exist.

---

## 8. Migrate and seed the database

```bash
cd /home/ubuntu/AssetFlow-AI
source .venv/bin/activate
alembic upgrade head
python -m app.seeding --profile demo --reset
```

Save the seeded login passwords printed in the terminal.

---

## 9. Build the frontend

```bash
cd /home/ubuntu/AssetFlow-AI/frontend
cp .env.production.example .env.production
# should contain: VITE_API_BASE_URL=/api/v1
npm install
npm run build
# output: frontend/dist/
```

---

## 10. Install systemd + nginx

```bash
# API service
sudo cp /home/ubuntu/AssetFlow-AI/deploy/assetflow.service /etc/systemd/system/assetflow.service
sudo systemctl daemon-reload
sudo systemctl enable --now assetflow
sudo systemctl status assetflow

# nginx site
sudo cp /home/ubuntu/AssetFlow-AI/deploy/nginx.conf /etc/nginx/sites-available/assetflow
sudo ln -sf /etc/nginx/sites-available/assetflow /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

If the repo path is not `/home/ubuntu/AssetFlow-AI`, edit both configs before copying.

---

## 11. Post-deploy checklist

| # | Check | URL / action | Expected |
|---|--------|--------------|----------|
| 1 | Liveness | `http://YOUR_EC2_PUBLIC_IP/health` | `{"status":"ok",...}` |
| 2 | Readiness | `http://YOUR_EC2_PUBLIC_IP/ready` | `"status":"ready"`, DB + ML ok |
| 3 | OpenAPI | `http://YOUR_EC2_PUBLIC_IP/docs` | Swagger UI |
| 4 | Frontend | `http://YOUR_EC2_PUBLIC_IP/` | Login page |
| 5 | Login | Seeded ADMIN | Dashboard loads |
| 6 | Dashboard | Operations / Dashboard | KPIs with data |
| 7 | ML | Operations → **Run AI pipeline** | Fleet health updates |
| 8 | Asset | Open `IT-LAP-0001` | Intelligence score |
| 9 | Assistant | “Which assets are high risk?” | Answer (template mode) |

---

## 12. Cost tip

- **Stop** the instance when not demoing: EC2 console → Instance state → Stop
- **Start** ~10 minutes before a viva / demo
- Elastic IP: free while attached to a running instance; small charge if allocated but unattached

---

## 13. Troubleshooting

**API not starting**

```bash
sudo journalctl -u assetflow -n 100 -f
```

Common causes: bad `DATABASE_URL`, missing `.venv`, wrong `WorkingDirectory` in the unit file.

**`/ready` returns 503 / ml_model not found**

- Confirm files exist:

```bash
ls -la /home/ubuntu/AssetFlow-AI/ml/artifacts/model.pt
ls -la /home/ubuntu/AssetFlow-AI/ml/artifacts/feature_stats.json
```

- Paths in `.env` must match; then `sudo systemctl restart assetflow`

**nginx 502 Bad Gateway**

- uvicorn down: `sudo systemctl status assetflow`
- Check nginx error log: `sudo tail -50 /var/log/nginx/error.log`

**Frontend blank / API 404**

- Rebuild with `VITE_API_BASE_URL=/api/v1` (relative path, not `http://127.0.0.1:8000`)
- Confirm `frontend/dist/index.html` exists and nginx `root` points at it

**CORS errors** (only if calling API from another origin)

- Set `CORS_ORIGINS=http://YOUR_EC2_PUBLIC_IP` in `.env` and restart: `sudo systemctl restart assetflow`

---

## Files in this folder

| File | Purpose |
|------|---------|
| [`nginx.conf`](nginx.conf) | SPA + API reverse proxy |
| [`assetflow.service`](assetflow.service) | systemd unit for uvicorn |
| [`.env.production.example`](.env.production.example) | Production env template (no secrets) |
| [`DEPLOY_AWS.md`](DEPLOY_AWS.md) | This guide |
