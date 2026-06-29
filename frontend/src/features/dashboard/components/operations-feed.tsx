import { Link } from "@tanstack/react-router";
import {
  ArrowRightLeft, UserPlus, Wrench, Package, Activity,
} from "lucide-react";

import { Card, CardHeader, EmptyState, Skeleton } from "@/components/ui-bits";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import { fmtRelative } from "@/lib/format";
import type { ActivityItem } from "@/lib/types/ui";
import { cn } from "@/lib/utils";

function activityIcon(type: string) {
  if (type.startsWith("ALLOCATION")) return <UserPlus className="size-3.5" />;
  if (type === "TRANSFER") return <ArrowRightLeft className="size-3.5" />;
  if (type.startsWith("MAINTENANCE")) return <Wrench className="size-3.5" />;
  if (type === "REGISTRATION") return <Package className="size-3.5" />;
  return <Activity className="size-3.5" />;
}

function activityTone(type: string): string {
  if (type.startsWith("MAINTENANCE")) return "bg-warning/15 text-[oklch(0.85_0.15_75)]";
  if (type === "TRANSFER") return "bg-monitor/15 text-[oklch(0.82_0.16_240)]";
  if (type.startsWith("ALLOCATION")) return "bg-success/15 text-[oklch(0.82_0.17_155)]";
  return "bg-primary/15 text-[oklch(0.82_0.18_285)]";
}

export function OperationsFeed({
  items,
  loading,
}: {
  items: ActivityItem[];
  loading?: boolean;
}) {
  return (
    <Card className={cn(glassCardClass(), "h-full max-h-80 flex flex-col")}>
      <CardHeader title="Operations feed" subtitle="Real-time lifecycle events" />
      <div className="flex-1 overflow-y-auto space-y-1 min-h-0">
        {loading ? (
          <><Skeleton className="h-11" /><Skeleton className="h-11" /><Skeleton className="h-11" /></>
        ) : items.length === 0 ? (
          <EmptyState title="No recent activity" />
        ) : (
          items.slice(0, 8).map((a) => {
            const type = a.activity_type ?? "";
            const row = (
              <div className="flex items-start gap-2.5 rounded-lg p-2 hover:bg-accent/20 transition-colors">
                <div className={cn("size-8 rounded-lg grid place-items-center shrink-0", activityTone(type))}>
                  {activityIcon(type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-medium leading-snug">{a.title}</div>
                  {a.subtitle && <div className="text-[10px] text-muted-foreground line-clamp-2 mt-0.5">{a.subtitle}</div>}
                </div>
                <span className="text-[10px] text-muted-foreground whitespace-nowrap shrink-0">
                  {fmtRelative(a.timestamp)}
                </span>
              </div>
            );
            return a.asset_id ? (
              <Link key={a.id} to="/assets/$id" params={{ id: String(a.asset_id) }} className="block">
                {row}
              </Link>
            ) : (
              <div key={a.id}>{row}</div>
            );
          })
        )}
      </div>
    </Card>
  );
}
