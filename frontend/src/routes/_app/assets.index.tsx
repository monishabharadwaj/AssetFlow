import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { MoreHorizontal, Pencil, Plus, Search, Trash2, Boxes } from "lucide-react";

import { Card, EmptyState, Pill, Skeleton } from "@/components/ui-bits";
import { AssetFormDialog } from "@/features/assets/components/asset-form-dialog";
import { useAssetsSearch, useDeactivateAsset } from "@/features/assets/hooks";
import { useDepartments } from "@/features/departments/hooks";
import { usePermissions } from "@/features/auth/use-permissions";
import { mapAssetForList } from "@/lib/adapters/assets";
import { MAX_PAGE_SIZE } from "@/lib/constants";
import { statusLabel, statusTone } from "@/lib/format";
import type { Asset, AssetStatus } from "@/lib/types/backend";
import { toast } from "@/lib/toast";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";

interface SearchParams {
  q?: string;
  status?: AssetStatus | "ALL";
  page?: number;
}

export const Route = createFileRoute("/_app/assets/")({
  validateSearch: (s: Record<string, unknown>): SearchParams => ({
    q: typeof s.q === "string" ? s.q : undefined,
    status: typeof s.status === "string" ? (s.status as SearchParams["status"]) : undefined,
    page: typeof s.page === "number" ? s.page : Number(s.page) || undefined,
  }),
  component: AssetsPage,
});

const STATUSES: (AssetStatus | "ALL")[] = ["ALL", "AVAILABLE", "ASSIGNED", "IN_MAINTENANCE", "RETIRED"];

function AssetsPage() {
  const search = Route.useSearch();
  const navigate = useNavigate({ from: "/assets" });
  const { can } = usePermissions();
  const canWrite = can("assets:write");
  const canReadDepts = can("departments:read");

  const [searchInput, setSearchInput] = useState(search.q ?? "");
  const [formOpen, setFormOpen] = useState(false);
  const [editAsset, setEditAsset] = useState<Asset | null>(null);

  const page = search.page ?? 1;
  const status = search.status ?? "ALL";

  const setSearch = (next: Partial<SearchParams>) =>
    void navigate({ search: (prev: SearchParams) => ({ ...prev, ...next }) as never });

  const query = useAssetsSearch({ q: search.q, status, page, page_size: 20 });
  const departments = useDepartments({ page: 1, page_size: MAX_PAGE_SIZE }, canReadDepts);
  const deptMap = new Map((departments.data?.items ?? []).map((d) => [d.id, d.name]));
  const deactivate = useDeactivateAsset();

  const list = (query.data?.items ?? []).map((a) => mapAssetForList(a, deptMap));
  const total = query.data?.total ?? list.length;

  const handleDeactivate = async (asset: Asset) => {
    if (!window.confirm(`Deactivate ${asset.asset_tag}?`)) return;
    try {
      await deactivate.mutateAsync(asset.id);
      toast("Asset deactivated");
    } catch (err) {
      toast((err as Error).message, "error");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Assets</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Manage and track all your assets · <span className="text-foreground/80">{total} total</span>
          </p>
        </div>
        {canWrite && (
          <Button onClick={() => { setEditAsset(null); setFormOpen(true); }} className="gap-2">
            <Plus className="size-4" /> Register Asset
          </Button>
        )}
      </div>

      <Card className="p-0">
        <div className="p-4 flex flex-wrap items-center gap-3 border-b border-border">
          <form
            onSubmit={(e) => { e.preventDefault(); setSearch({ q: searchInput || undefined, page: 1 }); }}
            className="relative flex-1 min-w-64"
          >
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <input
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search by tag, name, serial…"
              className="w-full h-9 pl-9 pr-3 rounded-lg bg-background border border-border text-sm focus:outline-none focus:ring-2 focus:ring-ring/50"
            />
          </form>
          <div className="flex items-center gap-1 rounded-lg border border-border p-1 bg-background/40">
            {STATUSES.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setSearch({ status: s, page: 1 })}
                className={`px-3 h-7 rounded-md text-xs ${status === s ? "bg-accent text-foreground" : "text-muted-foreground hover:text-foreground"}`}
              >
                {s === "ALL" ? "All" : statusLabel[s as AssetStatus]}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-card/95 backdrop-blur">
              <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground">
                <th className="px-4 py-2.5 font-medium">Tag</th>
                <th className="px-4 py-2.5 font-medium">Name</th>
                <th className="px-4 py-2.5 font-medium">Status</th>
                <th className="px-4 py-2.5 font-medium">Department</th>
                <th className="px-4 py-2.5 font-medium">Location</th>
                {canWrite && <th className="px-4 py-2.5 font-medium w-12" />}
              </tr>
            </thead>
            <tbody>
              {query.isLoading ? (
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i}><td colSpan={canWrite ? 6 : 5} className="px-4 py-3"><Skeleton className="h-6" /></td></tr>
                ))
              ) : list.length === 0 ? (
                <tr>
                  <td colSpan={canWrite ? 6 : 5}>
                    <EmptyState title="No assets found" hint="Try adjusting your search or filters." icon={<Boxes className="size-6" />} />
                  </td>
                </tr>
              ) : list.map((a, i) => (
                <tr
                  key={String(a.id)}
                  className={`border-t border-border hover:bg-accent/20 ${i % 2 === 1 ? "bg-background/20" : ""}`}
                >
                  <td className="px-4 py-2.5 font-mono text-xs">
                    <button
                      type="button"
                      className="hover:underline text-left"
                      onClick={() => navigate({ to: "/assets/$id", params: { id: String(a.id) } })}
                    >
                      {a.asset_tag}
                    </button>
                  </td>
                  <td className="px-4 py-2.5 font-medium">{a.name}</td>
                  <td className="px-4 py-2.5"><Pill tone={statusTone[a.status]}>{statusLabel[a.status]}</Pill></td>
                  <td className="px-4 py-2.5 text-muted-foreground">{a.department_name ?? "—"}</td>
                  <td className="px-4 py-2.5 text-muted-foreground">{a.location ?? "—"}</td>
                  {canWrite && (
                    <td className="px-4 py-2.5">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="size-8"><MoreHorizontal className="size-4" /></Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => navigate({ to: "/assets/$id", params: { id: String(a.id) } })}>
                            View
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => {
                            const raw = query.data?.items.find((x) => x.id === a.id);
                            if (raw) { setEditAsset(raw); setFormOpen(true); }
                          }}>
                            <Pencil className="size-3.5 mr-2" /> Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem className="text-destructive" onClick={() => {
                            const raw = query.data?.items.find((x) => x.id === a.id);
                            if (raw) void handleDeactivate(raw);
                          }}>
                            <Trash2 className="size-3.5 mr-2" /> Deactivate
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="px-4 py-3 border-t border-border flex items-center justify-between text-xs text-muted-foreground">
          <div>Showing {list.length} of {total}</div>
          <div className="flex items-center gap-1">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setSearch({ page: page - 1 })}
              className="h-8 px-3 rounded-md border border-border disabled:opacity-40 hover:bg-accent/40"
            >Prev</button>
            <span className="px-3">Page {page}</span>
            <button
              type="button"
              disabled={list.length < 20}
              onClick={() => setSearch({ page: page + 1 })}
              className="h-8 px-3 rounded-md border border-border disabled:opacity-40 hover:bg-accent/40"
            >Next</button>
          </div>
        </div>
      </Card>

      <AssetFormDialog open={formOpen} onOpenChange={setFormOpen} asset={editAsset} />
    </div>
  );
}
