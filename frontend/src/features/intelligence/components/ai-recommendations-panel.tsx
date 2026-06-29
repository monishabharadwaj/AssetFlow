import { useState } from "react";
import { Link } from "react-router-dom";
import { Clock, Sparkles, Wrench } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { Button } from "../../../shared/components/ui/button";
import { useToast } from "../../../shared/components/feedback/toast-provider";
import { useRecommendations } from "../hooks/use-intelligence";
import { usePermissions } from "../../auth/use-permissions";
import { usePipelineStatus, useRunPipeline } from "../../operations/hooks/use-operations";
import type { MaintenanceRecommendation } from "../api/intelligence-api";

const DISPLAY_LIMIT = 6;

const PRIORITY_LABELS: Record<MaintenanceRecommendation["priority"], string> = {
  HIGH: "Needs attention now",
  MEDIUM: "Plan soon",
  LOW: "When convenient",
};

const PRIORITY_ORDER: MaintenanceRecommendation["priority"][] = ["HIGH", "MEDIUM", "LOW"];

function priorityBadgeClass(priority: MaintenanceRecommendation["priority"]) {
  if (priority === "HIGH") return "bg-rose-50 text-rose-700";
  if (priority === "MEDIUM") return "bg-amber-50 text-amber-800";
  return "bg-muted text-muted-foreground";
}

function formatLastRun(iso: string | null | undefined) {
  if (!iso) return "Never";
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins} minutes ago`;
  return new Date(iso).toLocaleString();
}

export function AiRecommendationsPanel() {
  const { can } = usePermissions();
  const { toast } = useToast();
  const canRunIntelligence = can("intelligence:run");
  const [showAll, setShowAll] = useState(false);
  const [lastRunSummary, setLastRunSummary] = useState<string | null>(null);
  const fetchLimit = showAll ? 50 : DISPLAY_LIMIT;
  const { data, isLoading, isError, error, refetch } = useRecommendations(fetchLimit);
  const runPipeline = useRunPipeline();
  const { data: pipelineStatus } = usePipelineStatus();

  const visibleItems = data?.items ?? [];
  const hasMore = !showAll && (data?.total ?? 0) > DISPLAY_LIMIT;

  const grouped = PRIORITY_ORDER.map((priority) => ({
    priority,
    items: visibleItems.filter((item) => item.priority === priority),
  })).filter((group) => group.items.length > 0);

  async function handleRunScoring() {
    try {
      const result = await runPipeline.mutateAsync(true);
      const summary = `${result.scored} assets scored · ${result.drift_alerts} drift alerts · ${result.notifications_created} notifications · ${result.maintenance_auto_scheduled} maintenance auto-scheduled`;
      setLastRunSummary(summary);
      toast(`AI pipeline complete. ${summary}`);
      void refetch();
    } catch (err) {
      toast(err instanceof Error ? err.message : "AI scoring failed", "error");
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            AI Recommendations
          </CardTitle>
          <CardDescription>
            Plain-language maintenance priorities from the FT-Transformer health model
          </CardDescription>
          <p className="mt-2 flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            Last AI scored: {formatLastRun(pipelineStatus?.last_run_at)} ·{" "}
            {pipelineStatus?.scored_assets ?? 0} assets in cache
          </p>
        </div>
        {canRunIntelligence ? (
          <Button
            type="button"
            variant="secondary"
            size="sm"
            disabled={runPipeline.isPending}
            onClick={() => void handleRunScoring()}
          >
            {runPipeline.isPending ? "Running pipeline…" : "Run AI scoring"}
          </Button>
        ) : null}
      </CardHeader>
      <CardContent>
        {lastRunSummary ? (
          <div className="mb-4 rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-3 text-sm text-emerald-900">
            <p className="font-medium">Latest pipeline run</p>
            <p className="mt-1">{lastRunSummary}</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Updates predictions, drift alerts, notifications, and recommendations below.
            </p>
          </div>
        ) : null}
        {isError ? (
          <div className="rounded-md bg-rose-50 p-3 text-xs text-rose-800 border border-rose-200">
            <p className="font-semibold mb-1">Failed to load AI recommendations</p>
            <p>{error instanceof Error ? error.message : "An unexpected error occurred."}</p>
          </div>
        ) : isLoading ? (
          <p className="text-sm text-muted-foreground">Loading recommendations…</p>
        ) : !data?.items.length ? (
          <p className="text-sm text-muted-foreground">
            Run AI scoring to analyze your fleet with the FT-Transformer model. The pipeline scores every
            asset, detects health drift, creates notifications, and surfaces maintenance priorities here.
          </p>
        ) : (
          <div className="space-y-4">
            {grouped.map((group) => (
              <div key={group.priority} className="space-y-2">
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  {PRIORITY_LABELS[group.priority]}
                </p>
                {group.items.map((item) => (
                  <Link
                    key={`${item.asset_id}-${item.maintenance_type}`}
                    to={`/assets/${item.asset_id}?tab=maintenance`}
                    className="flex items-start gap-3 rounded-lg border p-3 transition-colors hover:bg-accent"
                  >
                    <Wrench className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium leading-snug">{item.title}</p>
                      {(item.asset_type_name || item.department_name) ? (
                        <p className="mt-0.5 text-xs font-medium text-foreground/80">
                          {[item.asset_type_name, item.department_name].filter(Boolean).join(" · ")}
                        </p>
                      ) : null}
                      <p className="mt-0.5 text-xs text-muted-foreground">{item.rationale}</p>
                    </div>
                    <span
                      className={`ml-auto shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium uppercase ${priorityBadgeClass(item.priority)}`}
                    >
                      {item.priority}
                    </span>
                  </Link>
                ))}
              </div>
            ))}
            {hasMore ? (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="w-full"
                onClick={() => setShowAll(true)}
              >
                {`View all ${data.total} recommendations`}
              </Button>
            ) : showAll && (data?.total ?? 0) > DISPLAY_LIMIT ? (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="w-full"
                onClick={() => setShowAll(false)}
              >
                Show fewer
              </Button>
            ) : null}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
