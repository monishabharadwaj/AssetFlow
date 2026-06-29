import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.core.database import SessionLocal
from sqlalchemy import func, select
from app.models.asset import AssetCategory, AssetType
from app.models.department import Department

db = SessionLocal()
try:
    print("Category count:", db.execute(select(func.count(AssetCategory.id))).scalar())
    print("Type count:", db.execute(select(func.count(AssetType.id))).scalar())
    print("Department count:", db.execute(select(func.count(Department.id))).scalar())
    
    print("\nCategories:")
    for cat in db.scalars(select(AssetCategory)).all():
        print(f" - {cat.id}: {cat.name}")
        
    print("\nDepartments:")
    for dept in db.scalars(select(Department)).all():
        print(f" - {dept.id}: {dept.name} (is_active={dept.is_active})")
finally:
    db.close()
