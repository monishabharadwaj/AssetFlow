import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  ArrowLeft, UserPlus, Undo2, ArrowRightLeft, Wrench,
} from "lucide-react";

import { Card, CardHeader, EmptyState, Pill, Skeleton } from "@/components/ui-bits";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { AssetHealthAnalysis } from "@/features/assets/components/asset-health-analysis";
import { AssetHealthTrendChart } from "@/features/assets/components/asset-health-trend-chart";
import { LifecycleActionSheet } from "@/features/assets/components/lifecycle-action-sheets";
import { AssetFormDialog } from "@/features/assets/components/asset-form-dialog";
import {
  useAsset,
  useAssetAllocations,
  useAssetMaintenance,
  useAssetTimeline,
  useAssetTransfers,
} from "@/features/assets/hooks";
import { usePermissions } from "@/features/auth/use-permissions";
import { useDepartments } from "@/features/departments/hooks";
import { MAX_PAGE_SIZE } from "@/lib/constants";
import { fmtDate, fmtRelative, statusLabel, statusTone } from "@/lib/format";
import type { AssetStatus } from "@/lib/types/backend";

const VALID_TABS = ["timeline", "allocations", "transfers", "maintenance", "health", "intelligence"] as const;
type DetailTab = (typeof VALID_TABS)[number];

interface DetailSearch {
  tab?: DetailTab;
}

export const Route = createFileRoute("/_app/assets/$id")({
  validateSearch: (s: Record<string, unknown>): DetailSearch => {
    const tab = typeof s.tab === "string" ? s.tab : undefined;
    return {
      tab: VALID_TABS.includes(tab as DetailTab) ? (tab as DetailTab) : undefined,
    };
  },
  component: AssetDetail,
});

type SheetKind = "assign" | "return" | "transfer" | "maintenance" | null;

function AssetDetail() {
  const { id } = Route.useParams();
  const { tab: tabSearch } = Route.useSearch();
  const { can } = usePermissions();
  const canWrite = can("assets:write");
  const canReadDepts = can("departments:read");

  const asset = useAsset(id);
  const timeline = useAssetTimeline(id);
  const allocations = useAssetAllocations(id);
  const transfers = useAssetTransfers(id);
  const maintenance = useAssetMaintenance(id);
  const departments = useDepartments({ page: 1, page_size: MAX_PAGE_SIZE }, canReadDepts);

  const [sheet, setSheet] = useState<SheetKind>(null);
  const [editOpen, setEditOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<DetailTab>(tabSearch ?? "timeline");

  useEffect(() => {
    if (tabSearch) setActiveTab(tabSearch);
  }, [tabSearch]);

  const a = asset.data;
  const deptName = canReadDepts
    ? departments.data?.items.find((d) => d.id === a?.current_department_id)?.name
    : undefined;

  const statusKey = a?.current_status as AssetStatus | undefined;
  const statusPillTone = statusKey && statusTone[statusKey] ? statusTone[statusKey] : "bg-muted text-muted-foreground border-border";
  const statusPillLabel = statusKey && statusLabel[statusKey] ? statusLabel[statusKey] : a?.current_status ?? "—";

  return (
    <div className="space-y-6">
      <Link to="/assets" className="text-xs text-muted-foreground hover:text-foreground inline-flex items-center gap-1">
        <ArrowLeft className="size-3.5" /> Back to assets
      </Link>

      {asset.isLoading ? (
        <Skeleton className="h-32" />
      ) : asset.isError ? (
        <EmptyState
          title="Asset not found or not accessible"
          hint={(asset.error as Error)?.message ?? "This asset may be outside your department scope."}
        />
      ) : !a ? (
        <EmptyState title="Asset not found" />
      ) : (
        <>
          <Card>
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <div className="text-xs font-mono text-muted-foreground">{a.asset_tag}</div>
                <h1 className="text-2xl font-semibold mt-1">{a.name}</h1>
                <div className="flex items-center gap-2 mt-2 flex-wrap">
                  <Pill tone={statusPillTone}>{statusPillLabel}</Pill>
                  {!a.is_active && <Pill tone="bg-muted text-muted-foreground border-border">Inactive</Pill>}
                </div>
              </div>
              {canWrite && (
                <div className="flex flex-wrap gap-2">
                  <Button variant="outline" size="sm" onClick={() => setEditOpen(true)}>Edit</Button>
                  {a.current_status === "AVAILABLE" && (
                    <Button variant="outline" size="sm" className="gap-1" onClick={() => setSheet("assign")}>
                      <UserPlus className="size-3.5" /> Assign
                    </Button>
                  )}
                  {a.current_status === "ASSIGNED" && (
                    <Button variant="outline" size="sm" className="gap-1" onClick={() => setSheet("return")}>
                      <Undo2 className="size-3.5" /> Return
                    </Button>
                  )}
                  <Button variant="outline" size="sm" className="gap-1" onClick={() => setSheet("transfer")}>
                    <ArrowRightLeft className="size-3.5" /> Transfer
                  </Button>
                  <Button variant="outline" size="sm" className="gap-1" onClick={() => setSheet("maintenance")}>
                    <Wrench className="size-3.5" /> Maintenance
                  </Button>
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <Field label="Location" value={a.current_location} />
              <Field label="Department" value={deptName ?? a.current_department_id} />
              <Field label="Serial" value={a.serial_number ?? "—"} />
              <Field label="Purchase" value={fmtDate(a.purchase_date)} />
              <Field label="Warranty" value={fmtDate(a.warranty_expiry)} />
              <Field label="Manufacturer" value={a.manufacturer ?? "—"} />
              <Field label="Model" value={a.model ?? "—"} />
              <Field label="Cost" value={a.purchase_cost} />
            </div>
          </Card>

          <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as DetailTab)}>
            <TabsList>
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
              <TabsTrigger value="allocations">Allocations</TabsTrigger>
              <TabsTrigger value="transfers">Transfers</TabsTrigger>
              <TabsTrigger value="maintenance">Maintenance</TabsTrigger>
              <TabsTrigger value="health">Health</TabsTrigger>
              <TabsTrigger value="intelligence">Intelligence</TabsTrigger>
            </TabsList>

            <TabsContent value="timeline" className="mt-4">
              <Card>
                {timeline.isLoading ? <Skeleton className="h-24" /> : (timeline.data?.items ?? []).length === 0 ? (
                  <EmptyState title="No timeline events" />
                ) : (
                  <div className="space-y-3">
                    {(timeline.data?.items ?? []).map((ev, i) => (
                      <div key={i} className="flex gap-3 text-sm border-b border-border pb-3 last:border-0">
                        <div className="text-[11px] text-muted-foreground w-28 shrink-0">{fmtRelative(ev.occurred_at)}</div>
                        <div>
                          <div className="font-medium">{ev.title}</div>
                          <div className="text-xs text-muted-foreground">{ev.event_type}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </TabsContent>

            <TabsContent value="allocations" className="mt-4">
              <Card>
                {(allocations.data?.items ?? []).length === 0 ? (
                  <EmptyState title="No allocation history" />
                ) : (
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-[11px] uppercase text-muted-foreground">
                        <th className="pb-2">Action</th>
                        <th className="pb-2">Employee</th>
                        <th className="pb-2">Allocated</th>
                        <th className="pb-2">Returned</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(allocations.data?.items ?? []).map((row) => (
                        <tr key={row.id} className="border-t border-border">
                          <td className="py-2">{row.action}</td>
                          <td className="py-2 text-muted-foreground">{row.employee_id}</td>
                          <td className="py-2">{fmtDate(row.allocated_at)}</td>
                          <td className="py-2">{fmtDate(row.returned_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </Card>
            </TabsContent>

            <TabsContent value="transfers" className="mt-4">
              <Card>
                {(transfers.data?.items ?? []).length === 0 ? (
                  <EmptyState title="No transfers" />
                ) : (
                  <div className="space-y-3 text-sm">
                    {(transfers.data?.items ?? []).map((t) => (
                      <div key={t.id} className="border-b border-border pb-3">
                        <div>{fmtDate(t.transferred_at)} — {t.from_location} → {t.to_location}</div>
                        {t.reason && <div className="text-xs text-muted-foreground mt-1">{t.reason}</div>}
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </TabsContent>

            <TabsContent value="maintenance" className="mt-4">
              <Card>
                {(maintenance.data?.items ?? []).length === 0 ? (
                  <EmptyState title="No maintenance records" />
                ) : (
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-[11px] uppercase text-muted-foreground">
                        <th className="pb-2">Type</th>
                        <th className="pb-2">Status</th>
                        <th className="pb-2">Scheduled</th>
                        <th className="pb-2">Description</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(maintenance.data?.items ?? []).map((m) => (
                        <tr key={m.id} className="border-t border-border">
                          <td className="py-2">{m.maintenance_type}</td>
                          <td className="py-2">{m.status}</td>
                          <td className="py-2">{fmtDate(m.scheduled_date)}</td>
                          <td className="py-2 text-muted-foreground">{m.description}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </Card>
            </TabsContent>

            <TabsContent value="health" className="mt-4">
              <Card>
                <CardHeader title="Health trend" subtitle="Score history over time" />
                <AssetHealthTrendChart assetId={id} />
              </Card>
            </TabsContent>

            <TabsContent value="intelligence" className="mt-4">
              <AssetHealthAnalysis
                assetId={id}
                assetTypeName={a.model ?? a.manufacturer ?? a.name}
                assetName={a.name}
              />
            </TabsContent>
          </Tabs>

          <LifecycleActionSheet asset={a} kind={sheet} onClose={() => setSheet(null)} />
          <AssetFormDialog open={editOpen} onOpenChange={setEditOpen} asset={a} />
        </>
      )}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <div className="text-[11px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="text-sm mt-1">{value}</div>
    </div>
  );
}
