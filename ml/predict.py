from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timezone

import torch
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.asset import Asset, AssetType
from ml.config import DEFAULT_FEATURE_STATS, DEFAULT_MODEL_PATH
from ml.data.schema import risk_level_from_score
from ml.etl.features import load_feature_stats, vectorize_row
from ml.etl.sources.database_source import DatabaseSource
from ml.models.ft_transformer import FTTransformer


def load_model(model_path=None):
  path = model_path or DEFAULT_MODEL_PATH
  checkpoint = torch.load(path, map_location="cpu", weights_only=False)
  model = FTTransformer(
      n_numeric=checkpoint["n_numeric"],
      n_categories=checkpoint["n_categories"],
  )
  model.load_state_dict(checkpoint["model_state"])
  model.eval()
  return model, checkpoint


def predict_from_features(
    features: dict,
    *,
    model_path=None,
    stats_path=None,
) -> dict:
  model, checkpoint = load_model(model_path)
  stats = load_feature_stats(stats_path or DEFAULT_FEATURE_STATS)
  numeric, cat_idx = vectorize_row(features, stats)

  with torch.no_grad():
    pred = model(
        torch.tensor(numeric).unsqueeze(0),
        torch.tensor([cat_idx]),
    ).item()

  risk = risk_level_from_score(pred)
  return {
      "health_score": round(pred, 4),
      "risk_level": risk,
      "model_version": checkpoint.get("model_version", "ft_transformer_v1"),
      "training_dataset": checkpoint.get("training_dataset", "synthetic_v1_80k"),
      "confidence": round(min(1.0, max(0.5, 1.0 - abs(pred - 0.5))), 4),
      "features_used": list(features.keys()),
  }


def predict_asset_by_tag(asset_tag: str) -> dict:
  db = SessionLocal()
  try:
    asset = db.execute(select(Asset).where(Asset.asset_tag == asset_tag)).scalar_one_or_none()
    if asset is None:
      raise ValueError(f"Asset not found: {asset_tag}")

    source = DatabaseSource(db)
    df = source.extract()
    asset_rows = df[df["synthetic_asset_id"] == str(asset.id)]
    if asset_rows.empty:
      raise ValueError(f"No feature history for asset: {asset_tag}")

    latest = asset_rows.iloc[-1].to_dict()
    result = predict_from_features(latest)
    result["asset_tag"] = asset_tag
    result["asset_id"] = str(asset.id)
    return result
  finally:
    db.close()


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(description="Predict asset health from operational DB")
  parser.add_argument("--asset-tag", required=True)
  args = parser.parse_args(argv)

  try:
    result = predict_asset_by_tag(args.asset_tag)
    print(result)
  except Exception as exc:
    print(f"Prediction failed: {exc}", file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
