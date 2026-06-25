from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

from ml.config import DATASET_NAME, DEFAULT_FEATURE_STATS, DEFAULT_MODEL_PATH, DEFAULT_TRAINING_DATASET, DEFAULT_TRAINING_REPORT
from ml.data.schema import LABEL_COLUMN, NUMERIC_FEATURE_COLUMNS, risk_level_from_score
from ml.etl.features import load_feature_stats
from ml.models.ft_transformer import FTTransformer, count_parameters


class TabularDataset(Dataset):
  def __init__(self, df: pd.DataFrame) -> None:
    self.numeric = df[[f"{c}_norm" for c in NUMERIC_FEATURE_COLUMNS]].values.astype(np.float32)
    self.category = df["asset_type_idx"].values.astype(np.int64)
    self.labels = df[LABEL_COLUMN].values.astype(np.float32)

  def __len__(self) -> int:
    return len(self.labels)

  def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    return (
        torch.tensor(self.numeric[idx]),
        torch.tensor(self.category[idx]),
        torch.tensor(self.labels[idx]),
    )


def risk_tier_accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
  true_tiers = [risk_level_from_score(float(v)) for v in y_true]
  pred_tiers = [risk_level_from_score(float(v)) for v in y_pred]
  return sum(a == b for a, b in zip(true_tiers, pred_tiers)) / len(true_tiers)


def train_model(
    *,
    dataset_path: Path | None = None,
    stats_path: Path | None = None,
    model_path: Path | None = None,
    report_path: Path | None = None,
    epochs: int = 30,
    batch_size: int = 512,
    lr: float = 1e-3,
    patience: int = 5,
    seed: int = 42,
) -> dict:
  torch.manual_seed(seed)
  np.random.seed(seed)

  ds_path = dataset_path or DEFAULT_TRAINING_DATASET
  stats_p = stats_path or DEFAULT_FEATURE_STATS
  model_p = model_path or DEFAULT_MODEL_PATH
  report_p = report_path or DEFAULT_TRAINING_REPORT

  df = pd.read_parquet(ds_path)
  stats = load_feature_stats(stats_p)

  train_df = df[df["split"] == "train"]
  val_df = df[df["split"] == "val"]
  test_df = df[df["split"] == "test"]

  train_loader = DataLoader(TabularDataset(train_df), batch_size=batch_size, shuffle=True)
  val_loader = DataLoader(TabularDataset(val_df), batch_size=batch_size)
  test_loader = DataLoader(TabularDataset(test_df), batch_size=batch_size)

  n_categories = len(stats["asset_type_categories"])
  model = FTTransformer(n_numeric=len(NUMERIC_FEATURE_COLUMNS), n_categories=n_categories)
  optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
  criterion = nn.MSELoss()

  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  model.to(device)

  best_val_mae = float("inf")
  best_state = None
  stale = 0
  history: list[dict] = []

  for epoch in range(1, epochs + 1):
    model.train()
    train_loss = 0.0
    for numeric, cat, labels in train_loader:
      numeric, cat, labels = numeric.to(device), cat.to(device), labels.to(device)
      optimizer.zero_grad()
      preds = model(numeric, cat)
      loss = criterion(preds, labels)
      loss.backward()
      optimizer.step()
      train_loss += loss.item() * len(labels)
    train_loss /= len(train_loader.dataset)

    model.eval()
    val_preds, val_labels = [], []
    with torch.no_grad():
      for numeric, cat, labels in val_loader:
        numeric, cat = numeric.to(device), cat.to(device)
        preds = model(numeric, cat)
        val_preds.extend(preds.cpu().numpy())
        val_labels.extend(labels.numpy())

    val_preds_arr = np.array(val_preds)
    val_labels_arr = np.array(val_labels)
    val_mae = float(np.mean(np.abs(val_preds_arr - val_labels_arr)))
    val_rmse = float(np.sqrt(np.mean((val_preds_arr - val_labels_arr) ** 2)))

    history.append({"epoch": epoch, "train_loss": train_loss, "val_mae": val_mae, "val_rmse": val_rmse})
    print(f"Epoch {epoch}: train_loss={train_loss:.4f} val_mae={val_mae:.4f}")

    if val_mae < best_val_mae:
      best_val_mae = val_mae
      best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
      stale = 0
    else:
      stale += 1
      if stale >= patience:
        print("Early stopping")
        break

  if best_state:
    model.load_state_dict(best_state)

  model.eval()
  test_preds, test_labels = [], []
  with torch.no_grad():
    for numeric, cat, labels in test_loader:
      numeric, cat = numeric.to(device), cat.to(device)
      preds = model(numeric, cat)
      test_preds.extend(preds.cpu().numpy())
      test_labels.extend(labels.numpy())

  test_preds_arr = np.array(test_preds)
  test_labels_arr = np.array(test_labels)
  test_mae = float(np.mean(np.abs(test_preds_arr - test_labels_arr)))
  test_rmse = float(np.sqrt(np.mean((test_preds_arr - test_labels_arr) ** 2)))
  ss_res = np.sum((test_labels_arr - test_preds_arr) ** 2)
  ss_tot = np.sum((test_labels_arr - test_labels_arr.mean()) ** 2)
  r2 = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0
  tier_acc = risk_tier_accuracy(test_labels_arr, test_preds_arr)

  model_p.parent.mkdir(parents=True, exist_ok=True)
  torch.save(
      {
          "model_state": model.state_dict(),
          "n_numeric": len(NUMERIC_FEATURE_COLUMNS),
          "n_categories": n_categories,
          "asset_type_categories": stats["asset_type_categories"],
          "model_version": "ft_transformer_v1",
          "training_dataset": DATASET_NAME,
      },
      model_p,
  )

  report = {
      "model_version": "ft_transformer_v1",
      "training_dataset": DATASET_NAME,
      "parameters": count_parameters(model),
      "best_val_mae": best_val_mae,
      "test_mae": test_mae,
      "test_rmse": test_rmse,
      "test_r2": r2,
      "risk_tier_accuracy": tier_acc,
      "epochs_run": len(history),
      "history": history,
  }
  report_p.write_text(json.dumps(report, indent=2), encoding="utf-8")
  return report


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(description="Train FT-Transformer health model")
  parser.add_argument("--epochs", type=int, default=30)
  parser.add_argument("--batch-size", type=int, default=512)
  args = parser.parse_args(argv)

  report = train_model(epochs=args.epochs, batch_size=args.batch_size)
  print(f"Test MAE: {report['test_mae']:.4f}, R2: {report['test_r2']:.4f}")
  if report["best_val_mae"] >= 0.07:
    print("Warning: val MAE >= 0.07 target", file=sys.stderr)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
