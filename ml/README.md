# AssetFlow AI — ML Pipeline

## Dual-dataset architecture

| Dataset | Command | Purpose |
|---------|---------|---------|
| **Operational (OLTP)** | `py -m app.seeding --profile demo --reset` | Application demo (~200 assets) |
| **AI Training** | `py -m ml.data --rows 80000 --assets 9000` | FT-Transformer training (`synthetic_v1_80k`) |

Training data is **file-based parquet** under `ml/artifacts/` — never loaded into PostgreSQL.

## Quick start

```bash
pip install -r requirements-ml.txt

# 1. Generate 80k training snapshots
py -m ml.data --rows 80000 --assets 9000 --history-months 24 --seed 42

# 2. ETL → normalized training dataset
py -m ml.etl --source file

# 3. Train FT-Transformer
py -m ml.train

# 4. Validate inference against operational DB
py -m app.seeding --profile demo --reset
py -m ml.predict --asset-tag IT-LAP-0001
```

## Feature schema

See `ml/data/schema.py` for the frozen column contract shared by synthetic generator, ETL, and inference.

## Health score formula

Documented in `ml/data/synthetic_generator.py` — causal lifecycle model with type-specific profiles in `ml/data/type_profiles.py`.
