import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

import { Card, CardHeader, EmptyState, Skeleton } from "@/components/ui-bits";
import { useAssetPreview } from "@/features/assets/asset-preview-context";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import type { FleetBands, HighRiskItem } from "@/features/dashboard/hooks/use-fleet-health-stats";
import { ChartTooltip } from "@/lib/chart-tooltip";
import { RISK_COLORS } from "@/lib/chart-theme";import { pct } from "@/lib/format";
import { cn } from "@/lib/utils";

const BAND_META = [
  { key: "critical" as const, label: "High risk", color: RISK_COLORS.critical },
  { key: "warning" as const, label: "Warning", color: RISK_COLORS.warning },
  { key: "monitor" as const, label: "Monitor", color: RISK_COLORS.monitor },
  { key: "healthy" as const, label: "Healthy / scored", color: RISK_COLORS.healthy },
  { key: "unscored" as const, label: "Not scored", color: "oklch(0.5 0.02 270)" },
];

export function FleetHealthHero({
  bands,
  scoredAssets,
  highRiskCount,
  highRiskItems,
  cacheWarm,
  loading,
  scoringPending,
  canRunAnalysis,
  onRunScoring,
  onRefreshAnalysis,
  scopeSubtitle,
}: {
  bands: FleetBands;
  scoredAssets: number;
  highRiskCount: number;
  highRiskItems: HighRiskItem[];
  cacheWarm: boolean;
  loading?: boolean;
  scoringPending?: boolean;
  canRunAnalysis?: boolean;
  onRunScoring?: () => void;
  onRefreshAnalysis?: () => void;
  scopeSubtitle: string;
}) {
  const { openPreview } = useAssetPreview();
  const chartBands: FleetBands & { unscored?: number } = bands;
  const data = BAND_META.map((b) => ({
    name: b.label,
    value: chartBands[b.key] ?? 0,
    color: b.color,
  })).filter((d) => d.value > 0);
  const total = data.reduce((a, b) => a + b.value, 0);

  return (
    <Card className={cn(glassCardClass(), "h-full max-h-64 overflow-hidden")}>
      <CardHeader title="Fleet health" subtitle={scopeSubtitle} />
      {loading ? (
        <Skeleton className="h-44" />      ) : !cacheWarm ? (
        <div className="space-y-2">
          <EmptyState title="Analysis cache is cold" hint="Run Refresh analysis to warm the cache." />
          {canRunAnalysis && onRefreshAnalysis && (
            <button type="button" onClick={onRefreshAnalysis} className="text-xs text-primary hover:underline">
              Refresh analysis →
            </button>
          )}
        </div>
      ) : scoringPending ? (
        <EmptyState title="Scoring in progress…" hint="Fleet bands will update when complete." />
      ) : total === 0 ? (
        <div className="space-y-2">
          <EmptyState title="No health data yet" hint="Run AI scoring to populate fleet health bands." />
          {canRunAnalysis && onRunScoring && (
            <button type="button" onClick={onRunScoring} className="text-xs text-primary hover:underline">
              Run AI scoring →
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-3 h-44">
          <div className="relative flex items-center justify-center">
            <div className="absolute -right-2 top-0 size-20 rounded-full bg-gradient-to-br from-[oklch(0.65_0.22_285)]/30 to-[oklch(0.6_0.2_245)]/10 blur-xl pointer-events-none" />
            <ResponsiveContainer width="100%" height={140}>
              <PieChart>
                <Pie data={data} dataKey="value" innerRadius={36} outerRadius={52} paddingAngle={2} stroke="none">
                  {data.map((d) => <Cell key={d.name} fill={d.color} />)}
                </Pie>
                <ChartTooltip />
              </PieChart>
            </ResponsiveContainer>            <div className="absolute inset-0 grid place-items-center pointer-events-none">
              <div className="text-center">
                <div className="text-lg font-semibold tabular-nums">{scoredAssets}</div>
                <div className="text-[9px] text-muted-foreground uppercase">Scored</div>
              </div>
            </div>
          </div>
          <div className="flex flex-col justify-between min-w-0 text-xs">
            <div className="space-y-1">
              {BAND_META.filter((b) => (chartBands[b.key] ?? 0) > 0).map((b) => (
                <div key={b.key} className="flex justify-between gap-1">
                  <span className="flex items-center gap-1.5 text-muted-foreground truncate">
                    <span className="size-2 rounded-full shrink-0" style={{ background: b.color }} />
                    {b.label}
                  </span>
                  <span className="tabular-nums font-medium">{chartBands[b.key]}</span>
                </div>
              ))}
            </div>
            <div>
              <div className="text-[10px] text-muted-foreground uppercase mb-1">Top high risk ({highRiskCount})</div>
              <ul className="space-y-0.5 max-h-20 overflow-y-auto">
                {highRiskItems.slice(0, 4).map((a) => (
                  <li key={a.asset_id}>
                    <button
                      type="button"
                      onClick={() =>
                        openPreview({
                          assetId: a.asset_id,
                          assetTag: a.asset_tag,
                          assetName: a.asset_name,
                          assetTypeName: a.asset_type_name,
                          healthScore: a.health_score,
                          riskLevel: a.risk_level,
                        })
                      }
                      className="hover:underline text-muted-foreground truncate block text-left w-full"
                    >
                      {a.asset_tag} — {pct(a.health_score)}
                    </button>
                  </li>
                ))}              </ul>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
