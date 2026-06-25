import { cn } from "../../lib/utils";

type HealthRingProps = {
  score: number | null | undefined;
  size?: number;
  strokeWidth?: number;
  className?: string;
};

function scoreColor(score: number): string {
  if (score >= 0.7) return "stroke-emerald-500";
  if (score >= 0.5) return "stroke-amber-500";
  return "stroke-rose-500";
}

export function HealthRing({
  score,
  size = 72,
  strokeWidth = 6,
  className,
}: HealthRingProps) {
  const normalized = score != null ? Math.min(1, Math.max(0, Number(score))) : null;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = normalized != null ? circumference * (1 - normalized) : circumference;
  const pct = normalized != null ? Math.round(normalized * 100) : null;

  return (
    <div className={cn("relative inline-flex items-center justify-center", className)} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={strokeWidth}
          className="stroke-muted"
        />
        {normalized != null ? (
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className={cn("transition-all", scoreColor(normalized))}
          />
        ) : null}
      </svg>
      <span className="absolute text-sm font-semibold tabular-nums">
        {pct != null ? `${pct}%` : "—"}
      </span>
    </div>
  );
}
