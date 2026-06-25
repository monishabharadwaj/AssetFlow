from __future__ import annotations

from typing import Protocol

import pandas as pd


class SourceAdapter(Protocol):
    def extract(self) -> pd.DataFrame: ...
