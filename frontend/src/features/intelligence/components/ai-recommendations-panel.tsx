import { useState } from "react";
import { Link } from "react-router-dom";
import { Wrench } from "lucide-react";
import sparkleIcon from "../../../assets/icons/sparkle.png";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../shared/components/ui/card";
import { Button } from "../../../shared/components/ui/button";
import { useRecommendations, useScoreBatch } from "../hooks/use-intelligence";
import type { MaintenanceRecommendation } from "../api/intelligence-api";

const DISPLAY_LIMIT = 6;

const PRIORITY_LABELS: Record<MaintenanceRecommendation["priority"], string> = {
  HIGH: "Needs attention now",
  MEDIUM: "Plan soon",
  LOW: "When convenient",
};

const PRIORITY_ORDER: MaintenanceRecommendation["priority"][] = [
  "HIGH",
  "MEDIUM",
  "LOW",
];

function priorityBadgeClass(priority: MaintenanceRecommendation["priority"]) {
  if (priority === "HIGH")
    return "bg-red-500/20 text-red-300 border border-red-500/30";

  if (priority === "MEDIUM")
    return "bg-amber-500/20 text-amber-300 border border-amber-500/30";

  return "bg-blue-500/20 text-blue-300 border border-blue-500/30";
}

export function AiRecommendationsPanel() {
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
    <Card className="rounded-2xl border border-slate-700 bg-[#111827] shadow-[0_0_25px_rgba(59,130,246,0.08)]">
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle className="flex items-center gap-3 text-xl font-semibold text-white">
            <img
              src={sparkleIcon}
              alt="Add Assets"
              className="h-14 w-14 object-contain
             transition-all duration-300
             drop-shadow-[0_0_12px_rgba(6,182,212,0.45)]
             hover:scale-105
             hover:drop-shadow-[0_0_20px_rgba(6,182,212,0.75)]"
            />
            AI Recommendations
          </CardTitle>
          <CardDescription className="text-slate-400">
            AI-generated maintenance priorities based on asset health
          </CardDescription>
        </div>
        <Button
          type="button"
          variant="secondary"
          size="sm"
          className="border-blue-500/30 bg-slate-900 text-blue-300 transition-all hover:border-blue-400 hover:bg-blue-500/10 hover:shadow-[0_0_18px_rgba(59,130,246,0.35)]"
          disabled={scoreBatch.isPending}
          onClick={() => void scoreBatch.mutateAsync(false)}
        >
          {scoreBatch.isPending ? "Scoring…" : "Run AI scoring"}
        </Button>
      </CardHeader>
      <CardContent>
        {isError ? (
          <div className="rounded-md bg-rose-50 p-3 text-xs text-rose-800 border border-rose-200">
            <p className="font-semibold mb-1">
              Failed to load AI recommendations
            </p>
            <p>
              {error instanceof Error
                ? error.message
                : "An unexpected error occurred."}
            </p>
          </div>
        ) : isLoading ? (
          <p className="text-sm text-muted-foreground">
            Loading recommendations…
          </p>
        ) : !data?.items.length ? (
          <p className="text-sm text-muted-foreground">
            Run AI scoring to surface maintenance priorities for your fleet.
            Overdue work orders appear here even before scoring, once they are
            due.
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
                    className="flex items-start gap-4 rounded-xl border border-slate-700 bg-slate-900/60 p-4 transition-all duration-300 hover:border-blue-500/30 hover:bg-slate-800 hover:shadow-[0_0_18px_rgba(59,130,246,0.20)]"
                  >
                    <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-800 shadow-[0_0_12px_rgba(245,158,11,0.20)]">
                      <Wrench className="h-5 w-5 text-amber-400" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold leading-snug text-white">
                        {item.title}
                      </p>
                      {item.asset_type_name || item.department_name ? (
                        <p className="mt-1 text-xs font-medium text-slate-300">
                          {[item.asset_type_name, item.department_name]
                            .filter(Boolean)
                            .join(" · ")}
                        </p>
                      ) : null}
                      <p className="mt-1 text-xs text-slate-400">
                        {item.rationale}
                      </p>
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
