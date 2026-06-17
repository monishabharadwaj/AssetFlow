from __future__ import annotations

import uuid

from app.repositories.timeline_repository import TimelineRepository
from app.schemas.timeline import AssetTimelineEvent, AssetTimelineResponse
from app.services.asset_service import AssetService


class TimelineService:
    def __init__(
        self,
        repository: TimelineRepository,
        asset_service: AssetService,
    ) -> None:
        self.repository = repository
        self.asset_service = asset_service

    def get_asset_timeline(
        self,
        asset_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
    ) -> AssetTimelineResponse:
        self.asset_service.get_by_id(asset_id)

        events: list[AssetTimelineEvent] = []

        for allocation in self.repository.allocations_for_asset(asset_id):
            events.append(
                AssetTimelineEvent(
                    event_type="ALLOCATION",
                    occurred_at=allocation.allocated_at,
                    title=f"{allocation.action.value.title()} asset allocation",
                    details={
                        "employee_id": str(allocation.employee_id),
                        "returned_at": allocation.returned_at.isoformat()
                        if allocation.returned_at
                        else None,
                        "notes": allocation.notes,
                    },
                )
            )

        for transfer in self.repository.transfers_for_asset(asset_id):
            events.append(
                AssetTimelineEvent(
                    event_type="TRANSFER",
                    occurred_at=transfer.transferred_at,
                    title="Asset transferred",
                    details={
                        "from_department_id": str(transfer.from_department_id),
                        "to_department_id": str(transfer.to_department_id),
                        "from_location": transfer.from_location,
                        "to_location": transfer.to_location,
                        "reason": transfer.reason,
                    },
                )
            )

        for maintenance in self.repository.maintenance_for_asset(asset_id):
            occurred_at = maintenance.updated_at
            events.append(
                AssetTimelineEvent(
                    event_type="MAINTENANCE",
                    occurred_at=occurred_at,
                    title="Maintenance record updated",
                    details={
                        "maintenance_type": maintenance.maintenance_type.value,
                        "status": maintenance.status.value,
                        "scheduled_date": maintenance.scheduled_date.isoformat()
                        if maintenance.scheduled_date
                        else None,
                        "completed_date": maintenance.completed_date.isoformat()
                        if maintenance.completed_date
                        else None,
                        "cost": float(maintenance.cost) if maintenance.cost is not None else None,
                    },
                )
            )

        for health in self.repository.health_history_for_asset(asset_id):
            events.append(
                AssetTimelineEvent(
                    event_type="HEALTH_SNAPSHOT",
                    occurred_at=health.recorded_at,
                    title="Asset health snapshot recorded",
                    details={
                        "health_score": float(health.health_score)
                        if health.health_score is not None
                        else None,
                        "condition_rating": health.condition_rating,
                        "failure_count": health.failure_count,
                        "depreciation_ratio": float(health.depreciation_ratio)
                        if health.depreciation_ratio is not None
                        else None,
                    },
                )
            )

        events.sort(key=lambda event: event.occurred_at, reverse=True)
        total = len(events)
        start = (page - 1) * page_size
        end = start + page_size
        paged_events = events[start:end]

        return AssetTimelineResponse.create(
            asset_id=asset_id,
            items=paged_events,
            total=total,
            page=page,
            page_size=page_size,
        )
