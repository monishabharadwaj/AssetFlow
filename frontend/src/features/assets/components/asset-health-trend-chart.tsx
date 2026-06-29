import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { EmptyState, Pill, Skeleton } from "@/components/ui-bits";
import { useAssetHealthHistory } from "@/features/assets/hooks";
import { chartTooltipStyle } from "@/lib/chart-theme";
import { bandTone, fmtDate, healthBand, pct } from "@/lib/format";

function toScore(value: string | number | null | undefined): number | null {
  if (value == null) return null;
  const n = typeof value === "number" ? value : Number(value);
  if (Number.isNaN(n)) return null;
  return n <= 1 ? n * 100 : n;
}

type Props = {
  assetId: string;
  /** Optional latest score to highlight after assessment */
  latestScore?: number | null;
};

export function AssetHealthTrendChart({ assetId, latestScore }: Props) {
  const history = useAssetHealthHistory(assetId);
  const items = [...(history.data?.items ?? [])].reverse();

  const chartData = items.map((h) => {
    const score = toScore(h.health_score);
    return {
      date: fmtDate(h.recorded_at),
      score,
    };
  }).filter((d) => d.score != null);

  const displayScore = latestScore != null
    ? toScore(latestScore)
    : chartData.length > 0 ? chartData[chartData.length - 1]!.score : null;

  if (history.isLoading) return <Skeleton className="h-48" />;

  return (
    <div className="space-y-3">
      {displayScore != null && (
        <div className="flex items-center gap-3">
          <div>
            <div className="text-xs text-muted-foreground uppercase">Latest health</div>
            <div className="text-2xl font-semibold tabular-nums">{pct(displayScore / 100)}</div>
          </div>
          <Pill tone={bandTone[healthBand(displayScore / 100)]}>{healthBand(displayScore / 100)}</Pill>
        </div>
      )}
      {chartData.length < 2 ? (
        <EmptyState title="Not enough history" hint="Health trend appears after multiple snapshots or assessments." />
      ) : (
        <div className="h-48">
          <ResponsiveContainer>
            <LineChart data={chartData}>
              <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="date" tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Line type="monotone" dataKey="score" stroke="oklch(0.7 0.22 285)" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
