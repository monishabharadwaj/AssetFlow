import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { PageHeader } from "../../../shared/components/data-display/page-header";
import { EntityDataTable, type ColumnDef } from "../../../shared/components/data-display/entity-data-table";
import { StatusBadge } from "../../../shared/components/data-display/status-badge";
import { EmptyState } from "../../../shared/components/feedback/empty-state";
import { buttonVariants } from "../../../shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { cn } from "../../../shared/lib/utils";
import { formatDate } from "../../../shared/lib/format";
import type { Asset } from "../../../shared/api/types";
import { fetchMaintenanceWorkQueue, type MaintenanceWorkQueueItem } from "../../intelligence/api/intelligence-api";
import { useDashboardSummary } from "../../dashboard/hooks/use-dashboard-summary";
import { useAssetsSearch } from "../../assets/hooks/use-assets";

export function MaintenancePageContent() {
  const { data: dashboard } = useDashboardSummary();
  const { data, isLoading, isError, error } = useAssetsSearch({
    page: 1,
    page_size: 50,
    current_status: "IN_MAINTENANCE",
  });

  const workQueue = useQuery({
    queryKey: ["maintenance", "work-queue"],
    queryFn: () => fetchMaintenanceWorkQueue(1, 30),
  });

  const queueColumns: ColumnDef<MaintenanceWorkQueueItem>[] = [
    {
      id: "tag",
      header: "Asset",
      cell: (row) => (
        <Link to={`/assets/${row.asset_id}?tab=maintenance`} className="font-medium text-primary hover:underline">
          {row.asset_tag}
        </Link>
      ),
    },
    { id: "name", header: "Name", cell: (row) => row.asset_name },
    { id: "type", header: "Type", cell: (row) => row.record.maintenance_type },
    { id: "status", header: "Status", cell: (row) => <StatusBadge status={row.record.status as Asset["current_status"]} /> },
    { id: "scheduled", header: "Scheduled", cell: (row) => formatDate(row.record.scheduled_date) },
    { id: "desc", header: "Description", cell: (row) => row.record.description },
  ];

  const columns: ColumnDef<Asset>[] = [
    {
      id: "tag",
      header: "Tag",
      cell: (row) => (
        <Link to={`/assets/${row.id}?tab=maintenance`} className="font-medium text-primary hover:underline">
          {row.asset_tag}
        </Link>
      ),
    },
    { id: "name", header: "Name", cell: (row) => row.name },
    { id: "status", header: "Status", cell: (row) => <StatusBadge status={row.current_status} /> },
    { id: "location", header: "Location", cell: (row) => row.current_location },
    {
      id: "actions",
      header: "",
      cell: (row) => (
        <Link
          to={`/assets/${row.id}?tab=maintenance`}
          className={cn(buttonVariants({ variant: "secondary", size: "sm" }))}
        >
          View Records
        </Link>
      ),
    },
  ];

  return (
    <div className="grid gap-4 md:gap-6">
      <PageHeader
        title="Maintenance Center"
        description="Track assets in maintenance and overdue work orders."
      />

      <Card>
        <CardHeader>
          <CardTitle>Overdue Work Queue</CardTitle>
          <CardDescription>
            {dashboard?.maintenance_due_count ?? 0} scheduled or in-progress records are due today or overdue.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {workQueue.isError ? (
            <EmptyState title="Failed to load work queue" />
          ) : (
            <EntityDataTable
              columns={queueColumns}
              data={workQueue.data?.items ?? []}
              isLoading={workQueue.isLoading}
              emptyMessage="No overdue maintenance records."
              rowKey={(r) => r.record.id}
            />
          )}
        </CardContent>
      </Card>

      <div>
        <h3 className="mb-3 text-lg font-semibold">Assets In Maintenance</h3>
        {isError ? (
          <EmptyState title="Failed to load" description={error?.message} />
        ) : (
          <EntityDataTable
            columns={columns}
            data={data?.items ?? []}
            isLoading={isLoading}
            emptyMessage="No assets currently in maintenance."
            rowKey={(r) => r.id}
          />
        )}
      </div>
    </div>
  );
}
