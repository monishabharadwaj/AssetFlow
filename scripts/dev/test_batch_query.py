import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.core.database import SessionLocal
from sqlalchemy import select
from app.models.health_history import AssetHealthHistory

print("Connecting...")
db = SessionLocal()
try:
    print("Running batch query...")
    start = time.time()
    stmt = (
        select(AssetHealthHistory)
        .distinct(AssetHealthHistory.asset_id)
        .order_by(AssetHealthHistory.asset_id, AssetHealthHistory.recorded_at.desc())
    )
    res = db.execute(stmt).scalars().all()
    duration = time.time() - start
    print(f"Batch query fetched {len(res)} items in {duration:.4f} seconds!")
except Exception as e:
    print("Error:", e)
finally:
    db.close()
