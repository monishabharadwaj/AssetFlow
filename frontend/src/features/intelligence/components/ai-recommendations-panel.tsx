import { useState } from "react";
import { Link } from "react-router-dom";
import { Sparkles, Wrench } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { Button } from "../../../shared/components/ui/button";
import { useRecommendations, useScoreBatch } from "../hooks/use-intelligence";
import { usePermissions } from "../../auth/use-permissions";
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

export function AiRecommendationsPanel() {
  const { can } = usePermissions();
  const canRunIntelligence = can("intelligence:run");
  const [showAll, setShowAll] = useState(false);
  const fetchLimit = showAll ? 50 : DISPLAY_LIMIT;
  const { data, isLoading, isError, error } = useRecommendations(fetchLimit);
  const scoreBatch = useScoreBatch();

  const visibleItems = data?.items ?? [];
  const hasMore = !showAll && (data?.total ?? 0) > DISPLAY_LIMIT;

  const grouped = PRIORITY_ORDER.map((priority) => ({
    priority,
    items: visibleItems.filter((item) => item.priority === priority),
  })).filter((group) => group.items.length > 0);

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            AI Recommendations
          </CardTitle>
          <CardDescription>Plain-language maintenance priorities from health predictions</CardDescription>
        </div>
        {canRunIntelligence ? (
          <Button
            type="button"
            variant="secondary"
            size="sm"
            disabled={scoreBatch.isPending}
            onClick={() => void scoreBatch.mutateAsync(false)}
          >
            {scoreBatch.isPending ? "Scoring…" : "Run AI scoring"}
          </Button>
        ) : null}
      </CardHeader>
      <CardContent>
        {isError ? (
          <div className="rounded-md bg-rose-50 p-3 text-xs text-rose-800 border border-rose-200">
            <p className="font-semibold mb-1">Failed to load AI recommendations</p>
            <p>{error instanceof Error ? error.message : "An unexpected error occurred."}</p>
          </div>
        ) : isLoading ? (
          <p className="text-sm text-muted-foreground">Loading recommendations…</p>
        ) : !data?.items.length ? (
          <p className="text-sm text-muted-foreground">
            Run AI scoring to surface maintenance priorities for your fleet. Overdue work orders appear
            here even before scoring, once they are due.
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
