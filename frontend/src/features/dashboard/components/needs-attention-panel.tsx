import { useMemo, useState } from "react";
import { Link } from "@tanstack/react-router";
import { AlertTriangle } from "lucide-react";
import { Card, CardHeader, EmptyState, Pill, Skeleton } from "@/components/ui-bits";
import { useAssetPreview } from "@/features/assets/asset-preview-context";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import type { AttentionItem } from "@/lib/types/ui";
import { cn } from "@/lib/utils";
const FILTER_CHIPS = [
  { id: "ALL", label: "All" },
  { id: "HIGH_RISK", label: "Asset health" },
  { id: "MAINTENANCE_DUE", label: "Maintenance" },
  { id: "IN_MAINTENANCE", label: "In service" },
] as const;

function severityTone(s: string): string {
  if (s === "Critical") return "bg-critical/15 text-[oklch(0.78_0.22_18)] border-critical/30";
  if (s === "High") return "bg-warning/15 text-[oklch(0.85_0.15_75)] border-warning/30";
  if (s === "Medium") return "bg-monitor/15 text-[oklch(0.82_0.16_240)] border-monitor/30";
  return "bg-muted text-muted-foreground border-border";
}

export function NeedsAttentionPanel({
  items,
  loading,
}: {
  items: AttentionItem[];
  loading?: boolean;
}) {
  const [filter, setFilter] = useState<string>("ALL");
  const { openPreview } = useAssetPreview();
  const filtered = useMemo(() => {
    if (filter === "ALL") return items;
    return items.filter((i) => i.item_type === filter);
  }, [items, filter]);

  return (
    <Card className={cn(glassCardClass(), "h-full max-h-80 flex flex-col")}>
      <CardHeader
        title="Needs attention"
        subtitle="Prioritized action items"
        action={<Link to="/assets" className="text-xs text-muted-foreground hover:text-foreground">View all</Link>}
      />
      <div className="flex flex-wrap gap-1.5 px-1 pb-2">
        {FILTER_CHIPS.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => setFilter(c.id)}
            className={cn(
              "text-[10px] px-2 py-0.5 rounded-full border transition-colors",
              filter === c.id
                ? "bg-primary/20 border-primary/40 text-foreground"
                : "border-border text-muted-foreground hover:bg-accent/40",
            )}
          >
            {c.label}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto space-y-2 min-h-0">
        {loading ? (
          <><Skeleton className="h-12" /><Skeleton className="h-12" /></>
        ) : filtered.length === 0 ? (
          <EmptyState title="All clear" hint="No items in this category." icon={<AlertTriangle className="size-5" />} />
        ) : (
          filtered.slice(0, 6).map((a) => {
            if (!a.asset_id) return null;
            const row = (
              <>
                <div className="size-7 rounded-md bg-critical/15 grid place-items-center shrink-0">
                  <AlertTriangle className="size-3.5 text-[oklch(0.78_0.22_18)]" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-medium truncate">{a.title}</div>
                  {a.subtitle && <div className="text-[10px] text-muted-foreground truncate">{a.subtitle}</div>}
                </div>
                <Pill tone={severityTone(a.severity)} className="text-[10px] shrink-0">{a.severity}</Pill>
              </>
            );
            if (a.item_type === "HIGH_RISK") {
              return (
                <button
                  key={a.id}
                  type="button"
                  onClick={() =>
                    openPreview({
                      assetId: String(a.asset_id),
                      assetTag: a.asset_tag ?? a.title,
                      assetName: a.asset_name ?? a.title,
                      riskLevel: "HIGH",
                    })
                  }
                  className="w-full flex items-center gap-2 rounded-lg border border-border/80 p-2.5 hover:bg-accent/30 transition-colors text-left"
                >
                  {row}
                </button>
              );
            }
            return (
              <Link
                key={a.id}
                to="/assets/$id"
                params={{ id: String(a.asset_id) }}
                className="flex items-center gap-2 rounded-lg border border-border/80 p-2.5 hover:bg-accent/30 transition-colors"
              >
                {row}
              </Link>
            );
          })        )}
      </div>
    </Card>
  );
}
