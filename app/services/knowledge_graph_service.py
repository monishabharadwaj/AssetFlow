from __future__ import annotations

import uuid

from app.exceptions.errors import NotFoundError
from app.repositories.asset_repository import AssetRepository
from app.repositories.timeline_repository import TimelineRepository
from app.schemas.operations import GraphEdge, GraphNode, KnowledgeGraphResponse
from app.services.asset_service import AssetService
from app.services.prediction_service import get_prediction_cache


class KnowledgeGraphService:
    def __init__(
        self,
        asset_service: AssetService,
        asset_repository: AssetRepository,
        timeline_repository: TimelineRepository,
    ) -> None:
        self.asset_service = asset_service
        self.asset_repository = asset_repository
        self.timeline_repository = timeline_repository

    def asset_neighborhood(self, asset_id: uuid.UUID) -> KnowledgeGraphResponse:
        asset = self.asset_repository.get_by_id(asset_id)
        if asset is None:
            raise NotFoundError("Asset", str(asset_id))
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        asset_node_id = str(asset.id)
        nodes.append(
            GraphNode(id=asset_node_id, label=f"{asset.name} ({asset.asset_tag})", node_type="ASSET")
        )

        dept = asset.current_department
        if dept:
            dept_id = str(dept.id)
            nodes.append(GraphNode(id=dept_id, label=dept.name, node_type="DEPARTMENT"))
            edges.append(GraphEdge(source=asset_node_id, target=dept_id, relationship="OWNED_BY"))

        employee = asset.current_assigned_employee
        if employee:
            emp_id = str(employee.id)
            emp_label = f"{employee.first_name} {employee.last_name}"
            nodes.append(GraphNode(id=emp_id, label=emp_label, node_type="EMPLOYEE"))
            edges.append(GraphEdge(source=emp_id, target=asset_node_id, relationship="ASSIGNED"))

        if asset.asset_type:
            type_id = f"type-{asset.asset_type.id}"
            nodes.append(
                GraphNode(id=type_id, label=asset.asset_type.name, node_type="ASSET_TYPE")
            )
            edges.append(GraphEdge(source=asset_node_id, target=type_id, relationship="IS_TYPE"))

        prediction = get_prediction_cache().get(str(asset.id))
        if prediction:
            risk_id = f"risk-{asset.id}"
            nodes.append(
                GraphNode(
                    id=risk_id,
                    label=f"Risk: {prediction.risk_level.value}",
                    node_type="AI_RISK",
                )
            )
            edges.append(GraphEdge(source=risk_id, target=asset_node_id, relationship="PREDICTS"))

        for transfer in self.timeline_repository.transfers_for_asset(asset_id)[:3]:
            to_dept_id = str(transfer.to_department_id)
            if not any(n.id == to_dept_id for n in nodes):
                nodes.append(
                    GraphNode(
                        id=to_dept_id,
                        label=transfer.to_department.name,
                        node_type="DEPARTMENT",
                    )
                )
            edges.append(
                GraphEdge(
                    source=asset_node_id,
                    target=to_dept_id,
                    relationship="TRANSFERRED_TO",
                )
            )

        return KnowledgeGraphResponse(
            center_id=asset_node_id,
            center_type="ASSET",
            nodes=nodes,
            edges=edges,
        )

    def department_high_risk(self, department_id: uuid.UUID) -> KnowledgeGraphResponse:
        from sqlalchemy import select

        from app.models.asset import Asset
        from app.models.department import Department

        db = self.asset_repository.db
        dept = db.get(Department, department_id)
        dept_name = dept.name if dept else "Department"
        dept_id = str(department_id)
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        cache = get_prediction_cache()

        assets = list(
            db.execute(
                select(Asset).where(
                    Asset.current_department_id == department_id,
                    Asset.is_active.is_(True),
                )
            )
            .scalars()
            .all()
        )

        nodes.append(GraphNode(id=dept_id, label=dept_name, node_type="DEPARTMENT"))

        for asset in assets:
            prediction = cache.get(str(asset.id))
            if prediction is None or prediction.risk_level.value != "HIGH":
                continue
            asset_id = str(asset.id)
            nodes.append(
                GraphNode(id=asset_id, label=f"{asset.name} ({asset.asset_tag})", node_type="ASSET")
            )
            edges.append(GraphEdge(source=dept_id, target=asset_id, relationship="HAS_HIGH_RISK_ASSET"))

        return KnowledgeGraphResponse(
            center_id=dept_id,
            center_type="DEPARTMENT",
            nodes=nodes,
            edges=edges,
        )
