from __future__ import annotations

import uuid

from app.repositories.timeline_repository import TimelineRepository
from app.schemas.timeline import AssetTimelineEvent, AssetTimelineResponse
from app.services import narrative as narr
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
        asset = self.asset_service.get_by_id(asset_id)
        asset_name = asset.name

        events: list[AssetTimelineEvent] = []

        for allocation in self.repository.allocations_for_asset(asset_id):
            employee = allocation.employee
            emp_name = narr.employee_display(employee.first_name, employee.last_name)
            title = narr.allocation_headline(
                allocation.action,
                asset_name=asset_name,
                asset_tag=asset.asset_tag,
                employee_name=emp_name,
            )
            events.append(
                AssetTimelineEvent(
                    event_type="ALLOCATION",
                    occurred_at=allocation.allocated_at,
                    title=title,
                    details={
                        "employee": emp_name,
                        "action": allocation.action.value,
                        "returned_at": allocation.returned_at.isoformat()
                        if allocation.returned_at
                        else None,
                        "notes": allocation.notes,
                    },
                )
            )

        for transfer in self.repository.transfers_for_asset(asset_id):
            from_name = transfer.from_department.name
            to_name = transfer.to_department.name
            title = f"{asset_name} moved to {to_name}"
            events.append(
                AssetTimelineEvent(
                    event_type="TRANSFER",
                    occurred_at=transfer.transferred_at,
                    title=title,
                    details={
                        "from_department": from_name,
                        "to_department": to_name,
                        "from_location": transfer.from_location,
                        "to_location": transfer.to_location,
                        "reason": transfer.reason,
                    },
                )
            )

        for maintenance in self.repository.maintenance_for_asset(asset_id):
            occurred_at = maintenance.updated_at
            mtype = maintenance.maintenance_type.value.replace("_", " ").title()
            if maintenance.status.value == "COMPLETED":
                title = f"{asset_name} completed {mtype.lower()} maintenance"
            else:
                title = f"{asset_name} — {mtype} maintenance {maintenance.status.value.replace('_', ' ').lower()}"
            events.append(
                AssetTimelineEvent(
                    event_type="MAINTENANCE",
                    occurred_at=occurred_at,
                    title=title,
                    details={
                        "type": mtype,
                        "status": maintenance.status.value.replace("_", " ").title(),
                        "scheduled_date": maintenance.scheduled_date.isoformat()
                        if maintenance.scheduled_date
                        else None,
                        "completed_date": maintenance.completed_date.isoformat()
                        if maintenance.completed_date
                        else None,
                        "cost": float(maintenance.cost) if maintenance.cost is not None else None,
                        "description": maintenance.description,
                    },
                )
            )

        for health in self.repository.health_history_for_asset(asset_id):
            score = float(health.health_score) if health.health_score is not None else None
            title = narr.health_snapshot_title(health_score=score)
            events.append(
                AssetTimelineEvent(
                    event_type="HEALTH_SNAPSHOT",
                    occurred_at=health.recorded_at,
                    title=title,
                    details={
                        "summary": narr.health_snapshot_message(
                            asset_name=asset_name,
                            health_score=score,
                            condition_rating=health.condition_rating,
                        ),
                        "health_score": score,
                        "condition_rating": health.condition_rating,
                        "failure_count": health.failure_count,
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
