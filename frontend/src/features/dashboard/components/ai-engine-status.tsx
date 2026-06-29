import { Activity, Sparkles } from "lucide-react";

import { Card } from "@/components/ui-bits";
import { usePipelineStatus } from "@/features/operations/hooks";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import { fmtRelative } from "@/lib/format";
import { cn } from "@/lib/utils";

export function AiEngineStatus({
  className,
  compact = false,
}: {
  className?: string;
  compact?: boolean;
}) {
  const { data, isLoading } = usePipelineStatus();

  if (isLoading || !data) return null;

  const online = data.cache_warm;

  return (
    <Card className={cn(glassCardClass(), compact ? "p-3" : "p-4", className)}>
      <div className="flex items-center gap-4">
        <div className="relative shrink-0">
          <div
            className={cn(
              "rounded-xl grid place-items-center",
              compact ? "size-10" : "size-14",
              "bg-gradient-to-br from-[oklch(0.65_0.22_285)]/40 to-[oklch(0.6_0.2_245)]/20",
              "border border-white/10 shadow-[0_0_24px_rgba(120,100,255,0.25)]",
            )}
            style={{ transform: "perspective(200px) rotateX(8deg) rotateY(-8deg)" }}
          >
            <Sparkles className={cn(compact ? "size-4" : "size-6", "text-[oklch(0.82_0.18_285)]")} />
          </div>
          {online && (
            <span className="absolute -top-1 -right-1 size-2.5 rounded-full bg-[oklch(0.72_0.17_155)] ring-2 ring-card animate-pulse" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={cn("font-semibold", compact ? "text-xs" : "text-sm")}>AI engine</span>
            <span
              className={cn(
                "text-[10px] px-2 py-0.5 rounded-full uppercase tracking-wide",
                online
                  ? "bg-success/15 text-[oklch(0.82_0.17_155)]"
                  : "bg-warning/15 text-[oklch(0.85_0.15_75)]",
              )}
            >
              {online ? "Online" : "Cold"}
            </span>
          </div>
          <ul className={cn("mt-1.5 space-y-0.5 text-muted-foreground", compact ? "text-[10px]" : "text-xs")}>
            <li className="flex items-center gap-1.5">
              <Activity className="size-3 shrink-0" />
              Models active · {data.scored_assets} assets scored
            </li>
            <li>Last run: {data.last_run_at ? fmtRelative(data.last_run_at) : "Never"}</li>
          </ul>
        </div>
      </div>
    </Card>
  );
}
