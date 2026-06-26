import { Activity, Cpu } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { usePipelineStatus } from "../hooks/use-operations";

function formatLastRun(iso: string | null) {
  if (!iso) return "Not yet run";
  return new Date(iso).toLocaleString();
}

export function PipelineStatusStrip() {
  const { data, isLoading } = usePipelineStatus();

  if (isLoading || !data) {
    return null;
  }

  return (
    <Card className="border-dashed">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-base">
          <Cpu className="h-4 w-4" />
          Autonomous AI pipeline
        </CardTitle>
        <CardDescription>
          {data.scheduler_enabled
            ? `Runs every ${data.scheduler_interval_minutes} min`
            : "Scheduler disabled — use Run AI scoring manually"}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-wrap gap-4 text-sm">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-muted-foreground" />
          <span>
            <span className="font-medium">{data.scored_assets}</span> assets scored
          </span>
        </div>
        <div>
          Last run: <span className="font-medium">{formatLastRun(data.last_run_at)}</span>
        </div>
        <div>
          Policy automation:{" "}
          <span className="font-medium">{data.policy_automation_enabled ? "On" : "Off"}</span>
        </div>
      </CardContent>
    </Card>
  );
}
