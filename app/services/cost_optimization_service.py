from __future__ import annotations

from app.repositories.asset_repository import AssetRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.schemas.operations import CostOptimizationItem, CostOptimizationResponse


class CostOptimizationService:
    def __init__(
        self,
        asset_repository: AssetRepository,
        maintenance_repository: MaintenanceRepository,
    ) -> None:
        self.asset_repository = asset_repository
        self.maintenance_repository = maintenance_repository

    def analyze(
        self, *, limit: int = 15, department_id=None
    ) -> CostOptimizationResponse:
        items: list[CostOptimizationItem] = []
        page = 1

        while len(items) < limit * 2:
            assets, total = self.asset_repository.list(
                page=page, page_size=100, is_active=True, department_id=department_id
            )
            if not assets:
                break
            for asset in assets:
                purchase = float(asset.purchase_cost)
                if purchase <= 0:
                    continue
                maint_spend = self.maintenance_repository.total_cost_for_asset(asset.id)
                ratio = maint_spend / purchase
                if ratio < 0.15 and maint_spend < 500:
                    continue

                priority = "HIGH" if ratio >= 0.5 else "MEDIUM" if ratio >= 0.3 else "LOW"
                recommendation = self._recommendation(
                    asset_name=asset.name,
                    ratio=ratio,
                    maint_spend=maint_spend,
                    purchase=purchase,
                )
                items.append(
                    CostOptimizationItem(
                        asset_id=str(asset.id),
                        asset_tag=asset.asset_tag,
                        asset_name=asset.name,
                        purchase_cost=round(purchase, 2),
                        maintenance_spend=round(maint_spend, 2),
                        tco_ratio=round(ratio, 3),
                        recommendation=recommendation,
                        priority=priority,
                    )
                )
            if page * 100 >= total:
                break
            page += 1

        items.sort(key=lambda i: -i.tco_ratio)
        return CostOptimizationResponse(items=items[:limit], total=len(items))

    def _recommendation(
        self,
        *,
        asset_name: str,
        ratio: float,
        maint_spend: float,
        purchase: float,
    ) -> str:
        pct = int(round(ratio * 100))
        base = (
            f"Lifetime service spend reached {pct}% of acquisition cost "
            f"(${maint_spend:,.0f} vs ${purchase:,.0f})."
        )
        if ratio >= 2.0:
            return (
                f"Data review recommended — cumulative service exceeds 2× acquisition cost. "
                f"{base} Replacement likely cheaper than the next 12 months of repairs."
            )
        if ratio >= 0.5:
            return f"{base} Replacement likely cheaper than the next 12 months of repairs."
        if ratio >= 0.3:
            return (
                f"{base} Review preventive maintenance strategy or plan replacement "
                f"within the next budget cycle."
            )
        return (
            f"{base} Monitor closely and consolidate service visits to slow TCO growth."
        )
