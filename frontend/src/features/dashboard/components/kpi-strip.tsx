import {
  Boxes, ShieldCheck, AlertTriangle, Siren, Wrench, Brain,
} from "lucide-react";

import { Card, Skeleton } from "@/components/ui-bits";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import type { FleetBands } from "@/features/dashboard/hooks/use-fleet-health-stats";
import { cn } from "@/lib/utils";

type KpiItem = {
  label: string;
  value: number | string;
  subtitle?: string;
  icon: React.ReactNode;
  tone: "primary" | "success" | "warning" | "critical" | "monitor" | "ai";
  sparkColor: string;
};

const toneBg: Record<string, string> = {
  primary: "bg-primary/15 text-[oklch(0.82_0.18_285)]",
  success: "bg-success/15 text-[oklch(0.82_0.17_155)]",
  warning: "bg-warning/15 text-[oklch(0.85_0.15_75)]",
  critical: "bg-critical/15 text-[oklch(0.78_0.22_18)]",
  monitor: "bg-monitor/15 text-[oklch(0.82_0.16_240)]",
  ai: "bg-[oklch(0.65_0.22_285)]/15 text-[oklch(0.82_0.18_285)]",
};

function pctOf(value: number, total: number): string {
  if (!total) return "—";
  return `${Math.round((value / total) * 100)}% of fleet`;
}

export function KpiStrip({
  loading,
  totalAssets,
  healthyCount,
  attentionCount,
  criticalCount,
  maintenanceDue,
  avgHealthPct,
  bands,
}: {
  loading?: boolean;
  totalAssets: number;
  healthyCount: number;
  attentionCount: number;
  criticalCount: number;
  maintenanceDue: number;
  avgHealthPct: number | null;
  bands: FleetBands;
}) {
  const scoredTotal = bands.healthy + bands.monitor + bands.warning + bands.critical;

  const items: KpiItem[] = [
    {
      label: "Total assets",
      value: totalAssets,
      subtitle: "Active in scope",
      icon: <Boxes className="size-4" />,
      tone: "primary",
      sparkColor: "from-[oklch(0.65_0.22_285)] to-[oklch(0.6_0.2_245)]",
    },
    {
      label: "Healthy assets",
      value: healthyCount || bands.healthy,
      subtitle: pctOf(bands.healthy, scoredTotal || totalAssets),
      icon: <ShieldCheck className="size-4" />,
      tone: "success",
      sparkColor: "from-[oklch(0.72_0.17_155)] to-[oklch(0.65_0.2_160)]",
    },
    {
      label: "Needs attention",
      value: attentionCount,
      subtitle: attentionCount ? "Action items" : "All clear",
      icon: <AlertTriangle className="size-4" />,
      tone: "warning",
      sparkColor: "from-[oklch(0.85_0.15_75)] to-[oklch(0.78_0.18_60)]",
    },
    {
      label: "High risk",
      value: criticalCount,
      subtitle: pctOf(criticalCount, scoredTotal || totalAssets),
      icon: <Siren className="size-4" />,
      tone: "critical",
      sparkColor: "from-[oklch(0.78_0.22_18)] to-[oklch(0.7_0.2_25)]",
    },
    {
      label: "Maintenance due",
      value: maintenanceDue,
      subtitle: maintenanceDue ? "Due soon" : "On schedule",
      icon: <Wrench className="size-4" />,
      tone: "monitor",
      sparkColor: "from-[oklch(0.7_0.16_240)] to-[oklch(0.65_0.18_270)]",
    },
    {
      label: "AI score (avg)",
      value: avgHealthPct != null ? `${avgHealthPct}%` : "—",
      subtitle: avgHealthPct != null ? "Fleet health estimate" : "Run scoring",
      icon: <Brain className="size-4" />,
      tone: "ai",
      sparkColor: "from-[oklch(0.7_0.22_285)] to-[oklch(0.65_0.2_300)]",
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
      {items.map((k) => (
        <Card key={k.label} className={cn(glassCardClass(), "hover:scale-[1.01] transition-transform")}>
          <div className="flex items-center justify-between">
            <div className={cn("size-9 rounded-lg grid place-items-center", toneBg[k.tone])}>{k.icon}</div>
          </div>
          <div className="mt-3">
            <div className="text-[11px] text-muted-foreground uppercase tracking-wide">{k.label}</div>
            {loading ? (
              <Skeleton className="h-8 w-16 mt-1" />
            ) : (
              <div className="text-2xl font-semibold tabular-nums mt-0.5">{k.value}</div>
            )}
            {k.subtitle && <div className="text-[10px] text-muted-foreground mt-0.5">{k.subtitle}</div>}
          </div>
          <div className={cn("mt-3 h-1 rounded-full bg-gradient-to-r opacity-60", k.sparkColor)} />
        </Card>
      ))}
    </div>
  );
}
