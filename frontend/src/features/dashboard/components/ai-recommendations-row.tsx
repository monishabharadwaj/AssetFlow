import { BarChart3, ChevronRight, Sparkles } from "lucide-react";

import { useAssetPreview } from "@/features/assets/asset-preview-context";
import { EmptyState, Pill, Skeleton } from "@/components/ui-bits";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import { priorityTone } from "@/lib/format";
import type { Recommendation } from "@/lib/types/ui";
import { cn } from "@/lib/utils";

const priorityBorder: Record<string, string> = {
  HIGH: "border-l-[oklch(0.78_0.22_18)]",
  MEDIUM: "border-l-[oklch(0.85_0.15_75)]",
  LOW: "border-l-[oklch(0.72_0.17_155)]",
};

export function AiRecommendationsRow({
  items,
  loading,
  headerAction,
}: {
  items: Recommendation[];
  loading?: boolean;
  headerAction?: React.ReactNode;
}) {
  const { openPreview } = useAssetPreview();

  return (
    <section className="space-y-3">
      <div className="flex items-end justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Sparkles className="size-4 text-[oklch(0.78_0.16_285)]" />
            AI recommendations
          </h2>
          <p className="text-sm text-muted-foreground">Smart insights and recommended actions</p>
        </div>
        {headerAction}
      </div>
      <div className="flex gap-3 overflow-x-auto pb-1 snap-x">
        {loading ? (
          Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-32 w-56 shrink-0 rounded-xl" />)
        ) : items.length === 0 ? (
          <div className="w-full">
            <EmptyState title="No recommendations" hint="Run analysis to generate guidance." icon={<BarChart3 className="size-5" />} />
          </div>
        ) : (
          items.slice(0, 6).map((r) => (
            <button
              key={String(r.id)}
              type="button"
              disabled={!r.asset_id}
              onClick={() => {
                if (!r.asset_id) return;
                openPreview({
                  assetId: String(r.asset_id),
                  assetTag: r.title,
                  assetName: r.description ?? r.title,
                  riskLevel: r.priority,
                });
              }}
              className={cn(
                "block text-left",
                !r.asset_id && "cursor-default",
              )}
            >
              <div
                className={cn(
                  glassCardClass(),
                  "shrink-0 w-56 p-4 border-l-4 hover:scale-[1.02] transition-transform snap-start",
                  priorityBorder[r.priority] ?? "border-l-border",
                  r.asset_id && "cursor-pointer",
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="size-8 rounded-lg bg-primary/15 grid place-items-center text-[oklch(0.82_0.18_285)]">
                    <BarChart3 className="size-4" />
                  </div>
                  <Pill tone={priorityTone[r.priority]} className="text-[10px]">{r.priority}</Pill>
                </div>
                <div className="mt-3 text-sm font-medium leading-tight line-clamp-2">{r.title}</div>
                {r.hint && <p className="text-[10px] text-muted-foreground mt-1.5 line-clamp-2">{r.hint}</p>}
                <div className="mt-3 text-[11px] text-primary flex items-center gap-0.5">
                  {r.asset_id ? "Preview" : "View"} <ChevronRight className="size-3" />
                </div>
              </div>
            </button>
          ))
        )}
      </div>
    </section>
  );
}
