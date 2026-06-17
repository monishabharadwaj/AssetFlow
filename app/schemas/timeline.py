from __future__ import annotations

import math
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AssetTimelineEvent(BaseModel):
    event_type: str
    occurred_at: datetime
    title: str
    details: dict[str, Any]


class AssetTimelineResponse(BaseModel):
    asset_id: uuid.UUID
    items: list[AssetTimelineEvent]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(
        cls,
        *,
        asset_id: uuid.UUID,
        items: list[AssetTimelineEvent],
        total: int,
        page: int,
        page_size: int,
    ) -> "AssetTimelineResponse":
        pages = math.ceil(total / page_size) if total > 0 else 0
        return cls(
            asset_id=asset_id,
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )
