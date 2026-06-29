import { createFileRoute, Link } from "@tanstack/react-router";
import { RefreshCw, Sparkles, ChevronRight } from "lucide-react";

import { Card } from "@/components/ui-bits";
import { AiEngineStatus } from "@/features/dashboard/components/ai-engine-status";
import { AiRecommendationsRow } from "@/features/dashboard/components/ai-recommendations-row";
import { AnalyticsOverviewRow } from "@/features/dashboard/components/analytics-overview-row";
import { DeptAllocationChart } from "@/features/dashboard/components/dept-allocation-chart";
import { FleetHealthHero } from "@/features/dashboard/components/fleet-health-hero";
import { KpiStrip } from "@/features/dashboard/components/kpi-strip";
import { MyWorkspaceHero } from "@/features/dashboard/components/my-workspace-hero";
import { NeedsAttentionPanel } from "@/features/dashboard/components/needs-attention-panel";
import { OperationsFeed } from "@/features/dashboard/components/operations-feed";
import { PriorityAlertsPanel } from "@/features/dashboard/components/priority-alerts-panel";
import { QuickActionsPanel } from "@/features/dashboard/components/quick-actions-panel";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import { useDashboardSummary, useFleetHealthStats, useMyWorkspace } from "@/features/dashboard/hooks";
import { useRecommendations, useRunScoreBatch } from "@/features/intelligence/hooks";
import { useRunPipeline } from "@/features/operations/hooks";
import { usePermissions } from "@/features/auth/use-permissions";
import { useAuth } from "@/lib/auth-context";
import { guardRoute } from "@/lib/route-guards";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/_app/dashboard")({
  beforeLoad: () => guardRoute("/dashboard"),
  component: Dashboard,
});

function Dashboard() {
  const { user } = useAuth();
  const { can } = usePermissions();
  const summary = useDashboardSummary();
  const fleet = useFleetHealthStats(true);
  const workspace = useMyWorkspace();
  const recs = useRecommendations();
  const refresh = useRunPipeline();
  const scoreBatch = useRunScoreBatch();

  const canRunAnalysis = can("intelligence:run");
  const isAdmin = user?.role === "ADMIN";
  const pipelineBusy = refresh.isPending || scoreBatch.isPending;

  const scopeLabel = user?.role === "ADMIN"
    ? "Organization-wide"
    : `${user?.department_name ?? "Your"} department`;

  const deptChartData = isAdmin
    ? fleet.departmentDistribution
    : fleet.departmentDistribution.filter((d) => d.name === user?.department_name);

  const runPipeline = () => {
    void refresh.mutate(undefined, {
      onSuccess: () => void scoreBatch.mutate(),
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Operations Center</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Fleet overview · <span className="text-foreground/80">{scopeLabel}</span>
          </p>
        </div>
        {canRunAnalysis && (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => refresh.mutate()}
              disabled={pipelineBusy}
              title="Re-run intelligence pipeline and persist results"
              className="h-9 px-3 rounded-lg border border-border hover:bg-accent/40 text-sm flex items-center gap-2 disabled:opacity-60"
            >
              <RefreshCw className={cn("size-4", refresh.isPending && "animate-spin")} />
              Refresh analysis
            </button>
            <button
              type="button"
              onClick={runPipeline}
              disabled={pipelineBusy}
              title="Refresh pipeline then batch-score all assets (may take 1–2 min)"
              className="h-9 px-4 rounded-lg bg-gradient-to-r from-[oklch(0.65_0.22_285)] to-[oklch(0.6_0.2_245)] text-white text-sm font-medium flex items-center gap-2 disabled:opacity-60 shadow-[0_0_20px_rgba(120,100,255,0.35)]"
            >
              <Sparkles className={cn("size-4", scoreBatch.isPending && "animate-pulse")} />
              {scoreBatch.isPending ? "Scoring…" : "Run AI pipeline"}
            </button>
          </div>
        )}
      </div>

      <MyWorkspaceHero workspace={workspace} scopeLabel={isAdmin ? scopeLabel : undefined} />

      <KpiStrip
        loading={fleet.isLoading}
        totalAssets={fleet.totalAssets}
        healthyCount={fleet.bands.healthy}
        attentionCount={fleet.attentionCount}
        criticalCount={fleet.highRiskCount}
        maintenanceDue={fleet.maintenanceDue}
        avgHealthPct={fleet.avgHealthPct}
        bands={fleet.bands}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        <FleetHealthHero
          bands={fleet.bands}
          scoredAssets={fleet.scoredAssets}
          highRiskCount={fleet.highRiskCount}
          highRiskItems={fleet.highRiskItems}
          cacheWarm={fleet.cacheWarm}
          loading={fleet.isLoading}
          scoringPending={scoreBatch.isPending}
          canRunAnalysis={canRunAnalysis}
          onRunScoring={() => scoreBatch.mutate()}
          onRefreshAnalysis={() => refresh.mutate()}
          scopeSubtitle={scopeLabel}
        />
        <NeedsAttentionPanel items={fleet.attentionItems} loading={summary.isLoading} />
        <OperationsFeed items={fleet.recentActivity} loading={summary.isLoading} />
      </div>

      <AnalyticsOverviewRow
        statusDistribution={fleet.statusDistribution}
        departmentData={deptChartData}
        recentActivity={fleet.recentActivity}
        avgHealthPct={fleet.avgHealthPct}
        isAdmin={isAdmin}
        loading={fleet.isLoading}
      />

      <AiRecommendationsRow
        items={recs.data ?? []}
        loading={recs.isLoading}
        headerAction={
          <Link to="/reports" className="text-xs text-muted-foreground hover:text-foreground inline-flex items-center gap-1">
            View report <ChevronRight className="size-3" />
          </Link>
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {isAdmin && (
          <DeptAllocationChart
            data={deptChartData}
            title="Assets by department"
            subtitle="Top departments"
            maxItems={6}
            compact
          />
        )}
        <PriorityAlertsPanel
          attentionItems={fleet.attentionItems}
          upcomingMaintenance={workspace.data?.upcoming_maintenance}
          loading={summary.isLoading}
        />
        {!isAdmin && (
          <Card className={cn(glassCardClass(), "p-4")}>
            <div className="text-xs text-muted-foreground uppercase mb-2">Your department</div>
            <div className="text-2xl font-semibold">{user?.department_name ?? "—"}</div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
              <div className="rounded-lg border border-border/80 p-2">
                <div className="text-[10px] text-muted-foreground">Assets</div>
                <div className="text-xl font-semibold tabular-nums">{fleet.totalAssets}</div>
              </div>
              <div className="rounded-lg border border-border/80 p-2">
                <div className="text-[10px] text-muted-foreground">Maintenance due</div>
                <div className="text-xl font-semibold tabular-nums">{fleet.maintenanceDue}</div>
              </div>
            </div>
          </Card>
        )}
      </div>

      <QuickActionsPanel />

      {canRunAnalysis && <AiEngineStatus compact />}
    </div>
  );
}
