import type { LucideIcon } from "lucide-react";
import { Link } from "react-router-dom";
import { Area, AreaChart, ResponsiveContainer } from "recharts";

import { cn } from "../../../shared/lib/utils";

const GLOW: Record<string, string> = {
  green: "kpi-glow-green border-emerald-500/20",
  blue: "kpi-glow-blue border-sky-500/20",
  amber: "kpi-glow-amber border-amber-500/20",
  red: "kpi-glow-red border-red-500/20",
  purple: "kpi-glow-purple border-violet-500/20",
  cyan: "kpi-glow-cyan border-cyan-500/20",
};

const ACCENT_TEXT: Record<string, string> = {
  green: "text-emerald-400",
  blue: "text-sky-400",
  amber: "text-amber-400",
  red: "text-red-400",
  purple: "text-violet-400",
  cyan: "text-cyan-400",
};

type PremiumKpiCardProps = {
  title: string;
  value: number | string;
  subtitle?: string | null;
  accent?: string;
  icon?: LucideIcon;
  href?: string;
  trend?: number[];
};

export function PremiumKpiCard({
  title,
  value,
  subtitle,
  accent = "blue",
  icon: Icon,
  href,
  trend = [],
}: PremiumKpiCardProps) {
  const display =
    typeof value === "number" && title.toLowerCase().includes("score")
      ? `${value}%`
      : typeof value === "number"
        ? value.toLocaleString()
        : value;

  const inner = (
    <div className={cn("premium-kpi-card glass-card rounded-xl border p-4", GLOW[accent] ?? GLOW.blue)}>
      <div className="flex items-start justify-between gap-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{title}</p>
        {Icon ? <Icon className={cn("h-4 w-4", ACCENT_TEXT[accent])} /> : null}
      </div>
      <p className={cn("mt-2 text-3xl font-semibold tabular-nums tracking-tight", ACCENT_TEXT[accent])}>
        {display}
      </p>
      {subtitle ? <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p> : null}
      {trend.length > 1 ? (
        <div className="mt-3 h-8">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trend.map((v, i) => ({ i, v }))}>
              <Area
                type="monotone"
                dataKey="v"
                stroke="currentColor"
                fill="currentColor"
                fillOpacity={0.1}
                strokeWidth={1.5}
                className={ACCENT_TEXT[accent]}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      ) : null}
    </div>
  );

  if (href) {
    return (
      <Link to={href} className="block">
        {inner}
      </Link>
    );
  }
  return inner;
}
