import { useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";

import { EntityDataTable, type ColumnDef } from "../../../shared/components/data-display/entity-data-table";
import { PaginationBar } from "../../../shared/components/data-display/pagination-bar";
import { StatusBadge } from "../../../shared/components/data-display/status-badge";
import { TimelineEventItem } from "../../../shared/components/data-display/timeline-event-item";
import { EmptyState } from "../../../shared/components/feedback/empty-state";
import { Skeleton } from "../../../shared/components/ui/skeleton";
import { Button } from "../../../shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { formatCurrency, formatDate } from "../../../shared/lib/format";
import type { Allocation, HealthHistory, Maintenance, Transfer } from "../../../shared/api/types";
import { useDepartment } from "../../departments/hooks/use-departments";
import { useEmployee } from "../../employees/hooks/use-employees";
import { useAsset } from "../hooks/use-assets";
import {
  useAssetAllocations,
  useAssetHealthHistory,
  useAssetMaintenanceList,
  useAssetTimeline,
  useAssetTransfers,
} from "../hooks/use-lifecycle";
import { LifecycleActionSheets } from "./lifecycle-action-sheets";

const TABS = ["overview", "timeline", "allocations", "transfers", "maintenance", "health"] as const;
type Tab = (typeof TABS)[number];

export function AssetDetailPageContent() {
  const { assetId = "" } = useParams<{ assetId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const tab = (searchParams.get("tab") as Tab) || "overview";
  const [page, setPage] = useState(1);

  const [assignOpen, setAssignOpen] = useState(false);
  const [transferOpen, setTransferOpen] = useState(false);
  const [maintenanceOpen, setMaintenanceOpen] = useState(false);
  const [healthOpen, setHealthOpen] = useState(false);

  const { data: asset, isLoading, isError, error } = useAsset(assetId);
  const { data: dept } = useDepartment(asset?.current_department_id ?? "");
  const { data: assignee } = useEmployee(asset?.current_assigned_employee_id ?? "");

  const timeline = useAssetTimeline(assetId, page, 20);
  const allocations = useAssetAllocations(assetId, page, 20);
  const transfers = useAssetTransfers(assetId, page, 20);
  const maintenance = useAssetMaintenanceList(assetId, page, 20);
  const health = useAssetHealthHistory(assetId, page, 20);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (isError || !asset) {
    return <EmptyState title="Asset not found" description={error?.message} />;
  }

  const setTab = (t: Tab) => {
    setPage(1);
    setSearchParams({ tab: t }, { replace: true });
  };

  const allocationColumns: ColumnDef<Allocation>[] = [
    { id: "action", header: "Action", cell: (r) => r.action },
    { id: "employee", header: "Employee", cell: (r) => r.employee_id.slice(0, 8) + "…" },
    { id: "allocated", header: "Allocated", cell: (r) => formatDate(r.allocated_at) },
    { id: "returned", header: "Returned", cell: (r) => formatDate(r.returned_at) },
  ];

  const transferColumns: ColumnDef<Transfer>[] = [
    { id: "from", header: "From Dept", cell: (r) => r.from_department_id.slice(0, 8) + "…" },
    { id: "to", header: "To Dept", cell: (r) => r.to_department_id.slice(0, 8) + "…" },
    { id: "location", header: "To Location", cell: (r) => r.to_location },
    { id: "date", header: "Date", cell: (r) => formatDate(r.transferred_at) },
  ];

  const maintenanceColumns: ColumnDef<Maintenance>[] = [
    { id: "type", header: "Type", cell: (r) => r.maintenance_type },
    { id: "status", header: "Status", cell: (r) => <StatusBadge status={r.status} /> },
    { id: "desc", header: "Description", cell: (r) => r.description },
    { id: "scheduled", header: "Scheduled", cell: (r) => formatDate(r.scheduled_date) },
  ];

  const healthColumns: ColumnDef<HealthHistory>[] = [
    { id: "date", header: "Recorded", cell: (r) => formatDate(r.recorded_at) },
    { id: "score", header: "Health Score", cell: (r) => r.health_score ?? "—" },
    { id: "rating", header: "Condition", cell: (r) => r.condition_rating ?? "—" },
    { id: "failures", header: "Failures", cell: (r) => r.failure_count },
  ];

  return (
    <div className="grid gap-4 md:gap-6">
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <div className="flex flex-wrap items-center gap-3">
                <CardTitle className="text-2xl">{asset.name}</CardTitle>
                <StatusBadge status={asset.current_status} />
              </div>
              <p className="mt-1 text-sm text-muted-foreground">Tag: {asset.asset_tag}</p>
              <div className="mt-3 flex flex-wrap gap-2 text-sm text-muted-foreground">
                <span className="rounded-md border px-2 py-1">{dept?.name ?? "Department"}</span>
                <span className="rounded-md border px-2 py-1">{asset.current_location}</span>
                {assignee ? (
                  <span className="rounded-md border px-2 py-1">
                    {assignee.first_name} {assignee.last_name}
                  </span>
                ) : null}
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button type="button" variant="secondary" onClick={() => setAssignOpen(true)}>
                {asset.current_status === "ASSIGNED" ? "Reassign" : "Assign"}
              </Button>
              <Button type="button" variant="secondary" onClick={() => setTransferOpen(true)}>
                Transfer
              </Button>
              <Button type="button" variant="secondary" onClick={() => setMaintenanceOpen(true)}>
                Maintenance
              </Button>
              <Button type="button" variant="secondary" onClick={() => setHealthOpen(true)}>
                Health
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      <div className="flex flex-wrap gap-2 border-b pb-2">
        {TABS.map((t) => (
          <Button
            key={t}
            type="button"
            variant={tab === t ? "default" : "ghost"}
            size="sm"
            onClick={() => setTab(t)}
            className="capitalize"
          >
            {t}
          </Button>
        ))}
      </div>

      {tab === "overview" ? (
        <Card>
          <CardContent className="grid gap-4 pt-6 sm:grid-cols-2 lg:grid-cols-3">
            <MetaItem label="Serial Number" value={asset.serial_number} />
            <MetaItem label="Manufacturer" value={asset.manufacturer} />
            <MetaItem label="Model" value={asset.model} />
            <MetaItem label="Purchase Date" value={formatDate(asset.purchase_date)} />
            <MetaItem label="Purchase Cost" value={formatCurrency(asset.purchase_cost)} />
            <MetaItem label="Warranty Expiry" value={formatDate(asset.warranty_expiry)} />
            <MetaItem label="Active" value={asset.is_active ? "Yes" : "No"} />
            <MetaItem label="Created" value={formatDate(asset.created_at)} />
          </CardContent>
        </Card>
      ) : null}

      {tab === "timeline" ? (
        <div className="space-y-3">
          {timeline.isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : timeline.data?.items.length === 0 ? (
            <EmptyState title="No timeline events" description="Lifecycle events will appear here." />
          ) : (
            timeline.data?.items.map((ev, i) => (
              <TimelineEventItem
                key={`${ev.event_type}-${ev.occurred_at}-${i}`}
                eventType={ev.event_type}
                title={ev.title}
                occurredAt={ev.occurred_at}
                details={ev.details}
              />
            ))
          )}
          {timeline.data ? (
            <PaginationBar
              page={timeline.data.page}
              pages={timeline.data.pages}
              total={timeline.data.total}
              pageSize={timeline.data.page_size}
              onPageChange={setPage}
            />
          ) : null}
        </div>
      ) : null}

      {tab === "allocations" ? (
        <>
          <EntityDataTable
            columns={allocationColumns}
            data={allocations.data?.items ?? []}
            isLoading={allocations.isLoading}
            rowKey={(r) => r.id}
          />
          {allocations.data ? (
            <PaginationBar
              page={allocations.data.page}
              pages={allocations.data.pages}
              total={allocations.data.total}
              pageSize={allocations.data.page_size}
              onPageChange={setPage}
            />
          ) : null}
        </>
      ) : null}

      {tab === "transfers" ? (
        <>
          <EntityDataTable
            columns={transferColumns}
            data={transfers.data?.items ?? []}
            isLoading={transfers.isLoading}
            rowKey={(r) => r.id}
          />
          {transfers.data ? (
            <PaginationBar
              page={transfers.data.page}
              pages={transfers.data.pages}
              total={transfers.data.total}
              pageSize={transfers.data.page_size}
              onPageChange={setPage}
            />
          ) : null}
        </>
      ) : null}

      {tab === "maintenance" ? (
        <>
          <EntityDataTable
            columns={maintenanceColumns}
            data={maintenance.data?.items ?? []}
            isLoading={maintenance.isLoading}
            rowKey={(r) => r.id}
          />
          {maintenance.data ? (
            <PaginationBar
              page={maintenance.data.page}
              pages={maintenance.data.pages}
              total={maintenance.data.total}
              pageSize={maintenance.data.page_size}
              onPageChange={setPage}
            />
          ) : null}
        </>
      ) : null}

      {tab === "health" ? (
        <>
          <EntityDataTable
            columns={healthColumns}
            data={health.data?.items ?? []}
            isLoading={health.isLoading}
            rowKey={(r) => r.id}
          />
          {health.data ? (
            <PaginationBar
              page={health.data.page}
              pages={health.data.pages}
              total={health.data.total}
              pageSize={health.data.page_size}
              onPageChange={setPage}
            />
          ) : null}
        </>
      ) : null}

      <LifecycleActionSheets
        asset={asset}
        assignOpen={assignOpen}
        transferOpen={transferOpen}
        maintenanceOpen={maintenanceOpen}
        healthOpen={healthOpen}
        onAssignOpenChange={setAssignOpen}
        onTransferOpenChange={setTransferOpen}
        onMaintenanceOpenChange={setMaintenanceOpen}
        onHealthOpenChange={setHealthOpen}
      />
    </div>
  );
}

function MetaItem({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground">{label}</p>
      <p className="text-sm">{value ?? "—"}</p>
    </div>
  );
}
