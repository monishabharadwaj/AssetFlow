import { Link } from "react-router-dom";

import { PageHeader } from "../../../shared/components/data-display/page-header";
import { EntityDataTable, type ColumnDef } from "../../../shared/components/data-display/entity-data-table";
import { StatusBadge } from "../../../shared/components/data-display/status-badge";
import { EmptyState } from "../../../shared/components/feedback/empty-state";
import { buttonVariants } from "../../../shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { cn } from "../../../shared/lib/utils";
import type { Asset } from "../../../shared/api/types";
import { useDashboardSummary } from "../../dashboard/hooks/use-dashboard-summary";
import { useAssetsSearch } from "../../assets/hooks/use-assets";

export function MaintenancePageContent() {
  const { data: dashboard } = useDashboardSummary();
  const { data, isLoading, isError, error } = useAssetsSearch({
    page: 1,
    page_size: 50,
    current_status: "IN_MAINTENANCE",
  });

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
          <CardTitle>Maintenance Due</CardTitle>
          <CardDescription>
            {dashboard?.maintenance_due_count ?? 0} scheduled or in-progress records are due today or
            overdue. Manage records from each asset&apos;s maintenance tab.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Link
            to="/assets?current_status=IN_MAINTENANCE"
            className={cn(buttonVariants({ variant: "secondary" }))}
          >
            View all in-maintenance assets
          </Link>
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
