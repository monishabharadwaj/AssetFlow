import { useMemo, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";

import { EntityDataTable, type ColumnDef } from "../../../shared/components/data-display/entity-data-table";
import { PaginationBar } from "../../../shared/components/data-display/pagination-bar";
import { StatusBadge } from "../../../shared/components/data-display/status-badge";
import {
  groupTimelineByDay,
  TimelineEventItem,
} from "../../../shared/components/data-display/timeline-event-item";
import { EmptyState } from "../../../shared/components/feedback/empty-state";
import { Skeleton } from "../../../shared/components/ui/skeleton";
import { Button } from "../../../shared/components/ui/button";
import { Card, CardContent } from "../../../shared/components/ui/card";
import { formatCurrency, formatDate } from "../../../shared/lib/format";
import { formatDayHeader } from "../../../shared/lib/date";
import type { Allocation, HealthHistory, Maintenance, Transfer } from "../../../shared/api/types";
import { useDepartmentsList } from "../../departments/hooks/use-departments";
import { useEmployeesList } from "../../employees/hooks/use-employees";
import { useAsset, useLookups } from "../hooks/use-assets";
import {
  useAssetAllocations,
  useAssetHealthHistory,
  useAssetMaintenanceList,
  useAssetTimeline,
  useAssetTransfers,
} from "../hooks/use-lifecycle";
import {
  useAssetRecommendations,
  usePredictHealth,
  useRunPrediction,
  useAssetRootCause,
} from "../../intelligence/hooks/use-intelligence";
import { AssetShowcaseCard } from "./asset-showcase-card";
import { HealthTrendChart } from "./health-trend-chart";
import { AssetHealthReport } from "./asset-health-report";
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
  const { types } = useLookups();
  const { data: departmentsData } = useDepartmentsList({ page: 1, page_size: 200 });
  const { data: employeesData } = useEmployeesList({ page: 1, page_size: 500 });

  const timeline = useAssetTimeline(assetId, page, 20);
  const allocations = useAssetAllocations(assetId, page, 20);
  const transfers = useAssetTransfers(assetId, page, 20);
  const maintenance = useAssetMaintenanceList(assetId, page, 20);
  const health = useAssetHealthHistory(assetId, page, 20);
  const latestHealth = useAssetHealthHistory(assetId, 1, 1);
  const prediction = usePredictHealth(assetId);
  const runPrediction = useRunPrediction(assetId);
  const assetRecommendations = useAssetRecommendations(assetId);
  const [explainLlm, setExplainLlm] = useState(false);
  const rootCause = useAssetRootCause(assetId, explainLlm, tab === "health");


  const departmentMap = useMemo(
    () => new Map((departmentsData?.items ?? []).map((d) => [d.id, d.name])),
    [departmentsData],
  );
  const employeeMap = useMemo(
    () =>
      new Map(
        (employeesData?.items ?? []).map((e) => [e.id, `${e.first_name} ${e.last_name}`]),
      ),
    [employeesData],
  );

  const typeName = types.data?.find((t) => t.id === asset?.asset_type_id)?.name;
  const departmentName = asset ? departmentMap.get(asset.current_department_id) : undefined;
  const assigneeName = asset?.current_assigned_employee_id
    ? employeeMap.get(asset.current_assigned_employee_id)
    : undefined;
  const healthScore = latestHealth.data?.items[0]?.health_score
    ? Number(latestHealth.data.items[0].health_score)
    : null;
  const predictedHealthScore = prediction.data?.health_score ?? null;
  const riskLevel = prediction.data?.risk_level ?? null;

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-40 w-full" />
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
    {
      id: "employee",
      header: "Employee",
      cell: (r) => employeeMap.get(r.employee_id) ?? "Unknown employee",
    },
    { id: "allocated", header: "Allocated", cell: (r) => formatDate(r.allocated_at) },
    { id: "returned", header: "Returned", cell: (r) => formatDate(r.returned_at) },
  ];

  const transferColumns: ColumnDef<Transfer>[] = [
    {
      id: "from",
      header: "From Dept",
      cell: (r) => departmentMap.get(r.from_department_id) ?? "Unknown",
    },
    {
      id: "to",
      header: "To Dept",
      cell: (r) => departmentMap.get(r.to_department_id) ?? "Unknown",
    },
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
    {
      id: "score",
      header: "Health Score",
      cell: (r) => (r.health_score != null ? `${Math.round(Number(r.health_score) * 100)}%` : "—"),
    },
    { id: "rating", header: "Condition", cell: (r) => r.condition_rating ?? "—" },
    { id: "failures", header: "Failures", cell: (r) => r.failure_count },
  ];

  const timelineGroups = timeline.data?.items
    ? groupTimelineByDay(timeline.data.items)
    : [];

  const actionButtons = (
    <>
      <Button type="button" variant="secondary" size="sm" onClick={() => setAssignOpen(true)}>
        {asset.current_status === "ASSIGNED" ? "Reassign" : "Assign"}
      </Button>
      <Button type="button" variant="secondary" size="sm" onClick={() => setTransferOpen(true)}>
        Transfer
      </Button>
      <Button type="button" variant="secondary" size="sm" onClick={() => setMaintenanceOpen(true)}>
        Maintenance
      </Button>
      <Button type="button" variant="secondary" size="sm" onClick={() => setHealthOpen(true)}>
        Health
      </Button>
      <Button
        type="button"
        variant="default"
        size="sm"
        disabled={runPrediction.isPending}
        onClick={() => void runPrediction.mutateAsync()}
      >
        {runPrediction.isPending ? "Assessing…" : "Run AI Assessment"}
      </Button>
    </>
  );

  return (
    <div className="grid gap-4 md:gap-6">
      <AssetShowcaseCard
        asset={asset}
        typeName={typeName}
        departmentName={departmentName}
        assigneeName={assigneeName}
        healthScore={healthScore}
        predictedHealthScore={predictedHealthScore}
        riskLevel={riskLevel}
        actions={actionButtons}
      />

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
        <div className="grid gap-4">
          <Card>
            <CardContent className="grid gap-4 pt-6 sm:grid-cols-2 lg:grid-cols-3">
              <MetaItem label="Serial Number" value={asset.serial_number} />
              <MetaItem label="Manufacturer" value={asset.manufacturer} />
              <MetaItem label="Model" value={asset.model} />
              <MetaItem label="Asset Type" value={typeName} />
              <MetaItem label="Purchase Date" value={formatDate(asset.purchase_date)} />
              <MetaItem label="Purchase Cost" value={formatCurrency(asset.purchase_cost)} />
              <MetaItem label="Warranty Expiry" value={formatDate(asset.warranty_expiry)} />
              <MetaItem label="Active" value={asset.is_active ? "Yes" : "No"} />
              <MetaItem label="Created" value={formatDate(asset.created_at)} />
            </CardContent>
          </Card>
          {assetRecommendations.data?.items.length ? (
            <Card>
              <CardContent className="space-y-2 pt-6">
                <h3 className="text-sm font-semibold">AI Recommendations</h3>
                {assetRecommendations.data.items.map((rec) => (
                  <div key={`${rec.asset_id}-${rec.maintenance_type}`} className="space-y-0.5">
                    <p className="text-sm font-medium">{rec.title}</p>
                    <p className="text-sm text-muted-foreground">{rec.rationale}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          ) : null}
        </div>
      ) : null}

      {tab === "timeline" ? (
        <div className="space-y-6">
          {timeline.isLoading ? (
            <Skeleton className="h-24 w-full" />
          ) : timelineGroups.length === 0 ? (
            <EmptyState title="No timeline events" description="Lifecycle events will appear here." />
          ) : (
            timelineGroups.map((group) => (
              <div key={group.day} className="space-y-3">
                <h3 className="text-sm font-semibold text-muted-foreground">
                  {formatDayHeader(group.day)}
                </h3>
                <div className="space-y-2">
                  {group.items.map((ev, i) => (
                    <TimelineEventItem
                      key={`${ev.event_type}-${ev.occurred_at}-${i}`}
                      eventType={ev.event_type}
                      title={ev.title}
                      occurredAt={ev.occurred_at}
                      details={ev.details}
                    />
                  ))}
                </div>
              </div>
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
          <AssetHealthReport
            assetName={asset.name}
            prediction={prediction.data ?? null}
            explanationSummary={rootCause.data?.root_cause_summary ?? null}
            enterpriseBrief={rootCause.data?.enterprise_brief ?? null}
            rootCause={rootCause.data ?? null}
            isExplainLoading={rootCause.isLoading || rootCause.isFetching}
            factors={rootCause.data?.factors ?? []}
            onExplain={() => {
              setExplainLlm(true);
              void rootCause.refetch();
            }}
          />
          <Card>
            <CardContent className="pt-6">
              <HealthTrendChart
                items={health.data?.items ?? []}
                predictedScore={predictedHealthScore}
              />
            </CardContent>
          </Card>
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
