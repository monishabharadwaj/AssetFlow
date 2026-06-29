import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import maintenanceIcon from "../../../assets/icons/maintenance.png";

import { PageHeader } from "../../../shared/components/data-display/page-header";
import {
  EntityDataTable,
  type ColumnDef,
} from "../../../shared/components/data-display/entity-data-table";
import { StatusBadge } from "../../../shared/components/data-display/status-badge";
import { EmptyState } from "../../../shared/components/feedback/empty-state";
import { buttonVariants } from "../../../shared/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../shared/components/ui/card";
import { cn } from "../../../shared/lib/utils";
import { formatDate } from "../../../shared/lib/format";
import type { Asset } from "../../../shared/api/types";
import {
  fetchMaintenanceWorkQueue,
  type MaintenanceWorkQueueItem,
} from "../../intelligence/api/intelligence-api";
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
        <Link
          to={`/assets/${row.asset_id}?tab=maintenance`}
          className="font-medium text-primary hover:underline"
        >
          {row.asset_tag}
        </Link>
      ),
    },
    { id: "name", header: "Name", cell: (row) => row.asset_name },
    { id: "type", header: "Type", cell: (row) => row.record.maintenance_type },
    {
      id: "status",
      header: "Status",
      cell: (row) => (
        <StatusBadge status={row.record.status as Asset["current_status"]} />
      ),
    },
    {
      id: "scheduled",
      header: "Scheduled",
      cell: (row) => formatDate(row.record.scheduled_date),
    },
    {
      id: "desc",
      header: "Description",
      cell: (row) => row.record.description,
    },
  ];

  const columns: ColumnDef<Asset>[] = [
    {
      id: "tag",
      header: "Tag",
      cell: (row) => (
        <Link
          to={`/assets/${row.id}?tab=maintenance`}
          className="font-medium text-primary hover:underline"
        >
          {row.asset_tag}
        </Link>
      ),
    },
    { id: "name", header: "Name", cell: (row) => row.name },
    {
      id: "status",
      header: "Status",
      cell: (row) => <StatusBadge status={row.current_status} />,
    },
    { id: "location", header: "Location", cell: (row) => row.current_location },
    {
      id: "actions",
      header: "",
      cell: (row) => (
        <Link
          to={`/assets/${row.id}?tab=maintenance`}
          className="rounded-lg border border-blue-500/30 bg-blue-600/10 px-3 py-2 text-blue-300 transition-all duration-300 hover:bg-blue-500/20 hover:text-white hover:shadow-[0_0_15px_rgba(59,130,246,0.45)]"
        >
          View Records
        </Link>
      ),
    },
  ];

  return (
    <div className="grid gap-4 md:gap-6">
      <div className="flex flex-col gap-4 rounded-3xl border border-slate-700 bg-[#111827] p-6 shadow-[0_0_25px_rgba(59,130,246,0.12)] md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-5">
          <img
            src={maintenanceIcon}
            alt="Maintenance"
            className="h-16 w-16 object-contain drop-shadow-[0_0_18px_rgba(59,130,246,0.55)]"
          />

          <div>
            <h2 className="text-3xl font-bold text-white">
              Maintenance Center
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Track assets in maintenance and overdue work orders.
            </p>
          </div>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Overdue Work Queue</CardTitle>
          <CardDescription>
            {dashboard?.maintenance_due_count ?? 0} scheduled or in-progress
            records are due today or overdue.
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
