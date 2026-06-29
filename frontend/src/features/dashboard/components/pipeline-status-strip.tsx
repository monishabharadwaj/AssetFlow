import { Activity } from "lucide-react";

import { usePipelineStatus } from "@/features/operations/hooks";
import { fmtRelative } from "@/lib/format";
import { cn } from "@/lib/utils";

export function PipelineStatusStrip({ className }: { className?: string }) {
  const { data, isLoading } = usePipelineStatus();

  if (isLoading || !data) return null;

  return (
    <div
      className={cn(
        "flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground rounded-lg border border-border px-3 py-2 bg-card/50",
        className,
      )}
    >
      <div className="flex items-center gap-1.5">
        <Activity className="size-3.5" />
        <span className="font-medium text-foreground">Analysis pipeline</span>
      </div>
      <span>
        Last run: {data.last_run_at ? fmtRelative(data.last_run_at) : "Never"}
      </span>
      <span>
        Cache: {data.cache_warm ? (
          <span className="text-[oklch(0.82_0.17_155)]">Warm</span>
        ) : (
          <span className="text-warning">Cold</span>
        )}
      </span>
      <span>Scored assets: <span className="tabular-nums text-foreground">{data.scored_assets}</span></span>
    </div>
  );
}
