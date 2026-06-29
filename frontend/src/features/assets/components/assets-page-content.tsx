import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Eye, Pencil, Plus, Trash2 } from "lucide-react";
import AssetsIcon from "../../../assets/icons/Assets.png";

import { PageHeader } from "../../../shared/components/data-display/page-header";
import {
  EntityDataTable,
  type ColumnDef,
} from "../../../shared/components/data-display/entity-data-table";
import {
  EntityFiltersBar,
  FilterField,
} from "../../../shared/components/data-display/entity-filters-bar";
import { PaginationBar } from "../../../shared/components/data-display/pagination-bar";
import { StatusBadge } from "../../../shared/components/data-display/status-badge";
import { ConfirmDialog } from "../../../shared/components/feedback/confirm-dialog";
import { EmptyState } from "../../../shared/components/feedback/empty-state";
import { useToast } from "../../../shared/components/feedback/toast-provider";
import { cn } from "../../../shared/lib/utils";
import { Button, buttonVariants } from "../../../shared/components/ui/button";
import { Input } from "../../../shared/components/ui/input";
import { Select } from "../../../shared/components/ui/select";
import { useUrlSearchParams } from "../../../shared/hooks/use-url-search-params";
import type { Asset, AssetStatus } from "../../../shared/api/types";
import { useDepartmentsList } from "../../departments/hooks/use-departments";
import {
  useAssetMutations,
  useAssetsList,
  useAssetsSearch,
} from "../hooks/use-assets";
import { AssetFormDialog } from "./asset-form-dialog";

const STATUS_OPTIONS: AssetStatus[] = [
  "AVAILABLE",
  "ASSIGNED",
  "IN_MAINTENANCE",
  "RETIRED",
  "DISPOSED",
];

const DEFAULT_PARAMS = {
  page: 1,
  page_size: 20,
  name: "",
  asset_tag: "",
  current_status: "",
  current_department_id: "",
  is_active: true,
};

export function AssetsPageContent() {
  const [searchParams] = useSearchParams();
  const createFromUrl = searchParams.get("create") === "true";

  const [params, setParams] = useUrlSearchParams(DEFAULT_PARAMS);
  const { toast } = useToast();
  const { deactivate } = useAssetMutations();
  const { data: deptData } = useDepartmentsList({ page: 1, page_size: 100 });

  const [formOpen, setFormOpen] = useState(createFromUrl);
  const [editAsset, setEditAsset] = useState<Asset | null>(null);
  const [deactivateId, setDeactivateId] = useState<string | null>(null);

  const hasSearchFilters =
    Boolean(params.name) ||
    Boolean(params.asset_tag) ||
    Boolean(params.current_status) ||
    Boolean(params.current_department_id);

  const listQuery = useAssetsList(
    {
      page: params.page,
      page_size: params.page_size,
      is_active: params.is_active,
    },
    !hasSearchFilters,
  );

  const searchQuery = useAssetsSearch(
    {
      page: params.page,
      page_size: params.page_size,
      name: params.name || undefined,
      asset_tag: params.asset_tag || undefined,
      current_status: (params.current_status as AssetStatus) || undefined,
      current_department_id: params.current_department_id || undefined,
    },
    hasSearchFilters,
  );

  const query = hasSearchFilters ? searchQuery : listQuery;
  const assets = query.data?.items ?? [];
  const deptMap = useMemo(
    () => new Map(deptData?.items.map((d) => [d.id, d.name]) ?? []),
    [deptData],
  );

  const columns: ColumnDef<Asset>[] = [
    {
      id: "tag",
      header: "Tag",
      cell: (row) => (
        <Link
          to={`/assets/${row.id}`}
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
    {
      id: "department",
      header: "Department",
      cell: (row) => deptMap.get(row.current_department_id) ?? "—",
    },
    { id: "location", header: "Location", cell: (row) => row.current_location },
    {
      id: "actions",
      header: "",
      className: "w-[120px]",
      cell: (row) => (
        <div className="flex justify-end gap-1">
          <Link
            to={`/assets/${row.id}`}
            className={cn(
              buttonVariants({ variant: "ghost", size: "icon" }),
              "rounded-xl text-slate-300 transition-all duration-300 hover:bg-blue-500/20 hover:text-blue-300 hover:shadow-[0_0_18px_rgba(59,130,246,0.45)]",
            )}
          >
            <Eye className="h-4 w-4" />
          </Link>
          <Button
            variant="ghost"
            size="icon"
            className="rounded-xl text-slate-300 transition-all duration-300 hover:bg-blue-500/20 hover:text-blue-300 hover:shadow-[0_0_18px_rgba(59,130,246,0.45)]"
            onClick={() => {
              setEditAsset(row);
              setFormOpen(true);
            }}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="rounded-xl text-red-400 transition-all duration-300 hover:bg-red-500/15 hover:text-red-300 hover:shadow-[0_0_18px_rgba(239,68,68,0.45)]"
            onClick={() => setDeactivateId(row.id)}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ];

  const handleDeactivate = async () => {
    if (!deactivateId) return;
    try {
      await deactivate.mutateAsync(deactivateId);
      toast("Asset deactivated");
      setDeactivateId(null);
    } catch (err) {
      toast(
        err instanceof Error ? err.message : "Failed to deactivate",
        "error",
      );
    }
  };

  return (
    <div className="grid gap-4 md:gap-6">
      <div className="flex flex-col gap-4 rounded-3xl border border-slate-700 bg-[#111827] p-6 shadow-[0_0_25px_rgba(59,130,246,0.12)] md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-5">
          <img
            src={AssetsIcon}
            alt="Assets"
            className="h-16 w-16 object-contain drop-shadow-[0_0_18px_rgba(59,130,246,0.55)]"
          />

          <div>
            <h2 className="text-3xl font-bold text-white">Assets</h2>

            <p className="mt-1 text-sm text-slate-400">
              Search, register and manage organizational assets.
            </p>
          </div>
        </div>

        <Button
          type="button"
          onClick={() => {
            setEditAsset(null);
            setFormOpen(true);
          }}
          className="rounded-xl border border-blue-500/40 bg-blue-600 px-4 text-white shadow-[0_0_18px_rgba(59,130,246,0.35)] transition-all duration-300 hover:bg-blue-500 hover:shadow-[0_0_22px_rgba(59,130,246,0.55)]"
        >
          <Plus className="mr-2 h-4 w-4" />
          Register Asset
        </Button>
      </div>
      <EntityFiltersBar>
        <FilterField label="Name" className="min-w-[160px] flex-1">
          <Input
            placeholder="Search by name"
            value={params.name}
            onChange={(e) => setParams({ name: e.target.value, page: 1 })}
          />
        </FilterField>
        <FilterField label="Asset Tag">
          <Input
            placeholder="Tag"
            value={params.asset_tag}
            onChange={(e) => setParams({ asset_tag: e.target.value, page: 1 })}
          />
        </FilterField>
        <FilterField label="Status">
          <Select
            value={params.current_status}
            onChange={(e) =>
              setParams({ current_status: e.target.value, page: 1 })
            }
          >
            <option value="">All statuses</option>
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {s.replace(/_/g, " ")}
              </option>
            ))}
          </Select>
        </FilterField>
        <FilterField label="Department">
          <Select
            value={params.current_department_id}
            onChange={(e) =>
              setParams({ current_department_id: e.target.value, page: 1 })
            }
          >
            <option value="">All departments</option>
            {deptData?.items.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </Select>
        </FilterField>
      </EntityFiltersBar>

      {query.isError ? (
        <EmptyState
          title="Failed to load assets"
          description={query.error?.message}
        />
      ) : (
        <>
          <EntityDataTable
            columns={columns}
            data={assets}
            isLoading={query.isLoading}
            emptyMessage="No assets match your filters."
            rowKey={(row) => row.id}
          />
          {query.data ? (
            <PaginationBar
              page={query.data.page}
              pages={query.data.pages}
              total={query.data.total}
              pageSize={query.data.page_size}
              onPageChange={(page) => setParams({ page })}
            />
          ) : null}
        </>
      )}

      <AssetFormDialog
        open={formOpen}
        onOpenChange={(open) => {
          setFormOpen(open);
          if (!open) setEditAsset(null);
        }}
        asset={editAsset}
      />

      <ConfirmDialog
        open={Boolean(deactivateId)}
        onOpenChange={(open) => !open && setDeactivateId(null)}
        title="Deactivate asset?"
        description="This will mark the asset as inactive. You can reactivate it later via edit."
        confirmLabel="Deactivate"
        destructive
        isConfirming={deactivate.isPending}
        onConfirm={handleDeactivate}
      />
    </div>
  );
}
