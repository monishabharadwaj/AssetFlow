from __future__ import annotations

import math

import torch
import torch.nn as nn


class FTTransformer(nn.Module):
  """Feature-tokenization transformer for tabular regression."""

  def __init__(
      self,
      n_numeric: int,
      n_categories: int,
      d_token: int = 64,
      n_heads: int = 4,
      n_layers: int = 3,
      dropout: float = 0.1,
  ) -> None:
    super().__init__()
    self.n_numeric = n_numeric
    self.n_categories = n_categories
    self.d_token = d_token

    self.category_embedding = nn.Embedding(n_categories, d_token)
    self.numeric_projection = nn.Linear(1, d_token)
    self.cls_token = nn.Parameter(torch.randn(1, 1, d_token))

    encoder_layer = nn.TransformerEncoderLayer(
        d_model=d_token,
        nhead=n_heads,
        dim_feedforward=d_token * 4,
        dropout=dropout,
        batch_first=True,
        activation="gelu",
    )
    self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
    self.head = nn.Sequential(
        nn.LayerNorm(d_token),
        nn.Linear(d_token, d_token // 2),
        nn.GELU(),
        nn.Dropout(dropout),
        nn.Linear(d_token // 2, 1),
        nn.Sigmoid(),
    )

  def forward(self, numeric: torch.Tensor, category_idx: torch.Tensor) -> torch.Tensor:
    # numeric: (B, n_numeric), category_idx: (B,)
    b = numeric.size(0)

    num_tokens = self.numeric_projection(numeric.unsqueeze(-1))
    cat_token = self.category_embedding(category_idx).unsqueeze(1)
    cls = self.cls_token.expand(b, -1, -1)

    tokens = torch.cat([cls, cat_token, num_tokens], dim=1)
    encoded = self.transformer(tokens)
    out = self.head(encoded[:, 0])
    return out.squeeze(-1)


def count_parameters(model: nn.Module) -> int:
  return sum(p.numel() for p in model.parameters() if p.requires_grad)
