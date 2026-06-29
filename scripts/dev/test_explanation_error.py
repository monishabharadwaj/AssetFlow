import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.services.prediction_explanation_service import PredictionExplanationService
from app.schemas.intelligence import RiskLevel

try:
    service = PredictionExplanationService()
    print("Building explanation...")
    explanation = service.build(
        features={"asset_type": "Laptop", "asset_age_days": 100},
        health_score=0.85,
        risk_level=RiskLevel.LOW,
        asset_name="Test Laptop"
    )
    print("Succeeded!")
except Exception as e:
    print("Failed with error:", type(e), e)
