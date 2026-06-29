import { useState } from "react";
import { Link } from "react-router-dom";
import {
  Activity,
  AlertTriangle,
  Brain,
  Calendar,
  DollarSign,
  FileText,
  Sparkles,
  TrendingDown,
} from "lucide-react";

import { useAuth } from "../../auth/auth-context";
import { usePermissions } from "../../auth/use-permissions";
import { useRunPipeline, useReportsAnalytics } from "../../operations/hooks/use-operations";
import { ReportBarChart } from "./report-bar-chart";
import { useToast } from "../../../shared/components/feedback/toast-provider";
import { Button } from "../../../shared/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../shared/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../../../shared/components/ui/table";
import { cn } from "../../../shared/lib/utils";

function formatLastRun(iso: string | null | undefined) {
  if (!iso) return "Never";
  const d = new Date(iso);
  const mins = Math.round((Date.now() - d.getTime()) / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins} min ago`;
  return d.toLocaleString();
}

function AiInsightBox({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-violet-500/20 bg-violet-500/5 p-4">
      <p className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-violet-700">
        <Brain className="h-3.5 w-3.5" />
        AI Analyst Insight
      </p>
      <p className="text-sm leading-relaxed text-foreground/90">{text}</p>
    </div>
  );
}

function KpiCard({ label, value, accent }: { label: string; value: string | number; accent?: string }) {
  return (
    <div className={cn("rounded-xl border bg-card p-4 shadow-sm", accent)}>
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums">{value}</p>
    </div>
  );
}

function formatAnalystSource(source: string, useAi: boolean, ollamaEnabled: boolean) {
  if (source === "ollama") return "AI analyst (Ollama)";
  if (!useAi) return "AI analyst (templates — AI Enhanced is off)";
  if (!ollamaEnabled) return "AI analyst (templates — Ollama disabled in server config)";
  return "AI analyst (templates — Ollama unavailable or request failed)";
}

export function ReportsPageContent() {
  const { user } = useAuth();
  const { can } = usePermissions();
  const { toast } = useToast();
  const canRunIntelligence = can("intelligence:run");
  const [aiToggleOn, setAiToggleOn] = useState(true);
  const useAi = canRunIntelligence ? aiToggleOn : true;
  const [lastPipelineSummary, setLastPipelineSummary] = useState<string | null>(null);
  const templateQuery = useReportsAnalytics(false);
  const aiQuery = useReportsAnalytics(true, { enabled: useAi });
  const runPipeline = useRunPipeline();

  const data = useAi && aiQuery.data ? aiQuery.data : templateQuery.data;
  const isLoading = templateQuery.isLoading && !templateQuery.data;
  const isEnhancing = useAi && (aiQuery.isFetching || aiQuery.isLoading) && !aiQuery.data;
  const isError = templateQuery.isError && !templateQuery.data;
  const error = templateQuery.error ?? aiQuery.error;
  const refetch = () => {
    void templateQuery.refetch();
    if (useAi) void aiQuery.refetch();
  };
  const isFetching = templateQuery.isFetching || (useAi && aiQuery.isFetching);

  const isAdmin = user?.role === "ADMIN";
  const reportTitle = isAdmin
    ? "Organization-wide report"
    : `${user?.department_name ?? "Department"} department report`;
  const reportSubtitle = isAdmin
    ? "Analytics across all departments and assets"
    : "Analytics for assets in your department only";

  async function handleRunScoring() {
    try {
      const result = await runPipeline.mutateAsync(true);
      const summary = `${result.scored} assets scored · ${result.drift_alerts} drift alerts · ${result.notifications_created} notifications · ${result.maintenance_auto_scheduled} maintenance auto-scheduled`;
      setLastPipelineSummary(summary);
      toast(`AI pipeline complete. ${summary}`);
      void refetch();
    } catch (err) {
      toast(err instanceof Error ? err.message : "AI scoring failed", "error");
    }
  }

  if (isLoading && !data) {
    return (
      <div className="space-y-2">
        <p className="text-sm text-muted-foreground">Loading analytics…</p>
        <p className="text-xs text-muted-foreground">
          Building KPIs, charts, and report sections from your fleet data.
        </p>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="space-y-2">
        <p className="text-sm text-destructive">Failed to load reports.</p>
        <p className="text-xs text-muted-foreground">
          {error instanceof Error ? error.message : "An unexpected error occurred."}
        </p>
        <Button type="button" variant="secondary" size="sm" onClick={() => void refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:gap-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Reports & Analytics</h2>
          <p className="text-sm font-medium text-foreground">{reportTitle}</p>
          <p className="text-sm text-muted-foreground">{reportSubtitle}</p>
          {!canRunIntelligence ? (
            <p className="mt-1 text-xs text-muted-foreground">
              AI narratives load automatically. Fleet scoring is managed by your department manager.
            </p>
          ) : null}
          <p className="mt-1 text-xs text-muted-foreground">
            Last AI scored: {formatLastRun(data.scoring.last_run_at)} · {data.scoring.scored_assets}{" "}
            assets in model cache · {formatAnalystSource(data.source, data.use_ai, data.ollama_enabled)}
            {data.ollama_enabled ? " · Ollama enabled" : " · Ollama disabled in config"}
            {isFetching ? " · Refreshing…" : ""}
          </p>
          {useAi && data.ollama_enabled && data.source === "analyst_template" ? (
            <p className="mt-1 text-xs text-amber-700">
              Ollama is configured but this report used template text. Ensure Ollama is running at
              localhost:11434 with your model pulled, then refresh.
            </p>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-2">
          {canRunIntelligence ? (
            <>
              <Button
                type="button"
                variant={aiToggleOn ? "default" : "secondary"}
                size="sm"
                onClick={() => setAiToggleOn((v) => !v)}
              >
                <Sparkles className="mr-2 h-4 w-4" />
                {aiToggleOn ? "AI Enhanced: On" : "AI Enhanced: Off"}
              </Button>
              <Button
                type="button"
                variant="secondary"
                size="sm"
                disabled={runPipeline.isPending}
                onClick={() => void handleRunScoring()}
              >
                <Activity className="mr-2 h-4 w-4" />
                {runPipeline.isPending ? "Running AI pipeline…" : "Run AI Scoring"}
              </Button>
            </>
          ) : null}
        </div>
      </div>

      {isEnhancing ? (
        <div className="rounded-lg border border-violet-500/30 bg-violet-500/5 p-3 text-sm">
          <p className="font-medium text-violet-900">Enhancing report with Ollama…</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Template analytics are shown below. AI narratives will refresh when Ollama finishes (may take up to
            a minute).
          </p>
        </div>
      ) : null}

      {useAi && aiQuery.isError && templateQuery.data ? (
        <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3 text-sm text-amber-900">
          <p className="font-medium">Ollama enhancement timed out or failed</p>
          <p className="mt-1 text-xs">
            Showing template analytics. Ensure Ollama is running, then click Retry or toggle AI Enhanced off and on.
          </p>
        </div>
      ) : null}

      {lastPipelineSummary ? (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-4 text-sm">
          <p className="font-medium text-emerald-900">Latest AI pipeline run</p>
          <p className="mt-1">{lastPipelineSummary}</p>
          <p className="mt-1 text-xs text-muted-foreground">
            Predictions, drift alerts, KPIs, and recommendations below have been refreshed.
          </p>
        </div>
      ) : null}

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <KpiCard label="Active assets" value={data.kpis.active_assets} />
        <KpiCard label="Avg fleet health" value={`${data.kpis.avg_fleet_health_pct}%`} accent="border-emerald-500/20" />
        <KpiCard label="High risk" value={data.kpis.high_risk_assets} accent="border-rose-500/20" />
        <KpiCard label="Maintenance due" value={data.kpis.maintenance_due} accent="border-amber-500/20" />
        <KpiCard label="Drift alerts" value={data.kpis.drift_alerts} />
        <KpiCard
          label="Est. savings"
          value={`$${Number(data.kpis.estimated_annual_savings ?? data.cost.estimated_annual_savings).toLocaleString()}`}
          accent="border-sky-500/20"
        />
      </div>

      {data.benchmarks ? (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <KpiCard
            label="Company avg health"
            value={`${data.benchmarks.org_avg_fleet_health_pct}%`}
            accent="border-slate-500/20"
          />
          <KpiCard
            label="Dept health vs company avg"
            value={`${data.benchmarks.dept_vs_org_health_delta >= 0 ? "+" : ""}${data.benchmarks.dept_vs_org_health_delta}%`}
            accent={
              data.benchmarks.dept_vs_org_health_delta >= 0
                ? "border-emerald-500/20"
                : "border-rose-500/20"
            }
          />
          <KpiCard
            label="Company high-risk assets"
            value={data.benchmarks.org_high_risk_assets}
            accent="border-amber-500/20"
          />
        </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Executive AI Report
          </CardTitle>
          <CardDescription>
            {formatAnalystSource(data.source, data.use_ai, data.ollama_enabled)}
            {useAi && data.source === "ollama"
              ? " — executive sections enhanced by Ollama"
              : useAi
                ? " — toggle AI Enhanced on and ensure Ollama is running for LLM narratives"
                : " — turn on AI Enhanced for Ollama-powered narratives"}
          </CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4 lg:grid-cols-2">
          {data.executive_sections.map((section) => (
            <div key={section.key} className="rounded-lg border p-4">
              <h3 className="font-semibold">{section.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{section.summary}</p>
              {section.bullets.length ? (
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                  {section.bullets.map((b) => (
                    <li key={b}>{b}</li>
                  ))}
                </ul>
              ) : null}
            </div>
          ))}
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5" />
              Health Drift
            </CardTitle>
            <CardDescription>
              {data.drift.deteriorating.length} deteriorating · {data.drift.improving_count} improving
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <AiInsightBox text={data.drift.ai_insight} />
            <ReportBarChart
              data={data.drift.health_trend_chart}
              valueLabel="Health change %"
              color="#ef4444"
            />
            <div>
              <p className="mb-2 text-xs font-medium uppercase text-muted-foreground">Dept health comparison</p>
              <ReportBarChart
                data={data.drift.department_comparison}
                valueLabel="Avg health %"
                color="#8b5cf6"
                height={180}
              />
            </div>
            {data.drift.key_factors.length ? (
              <ul className="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                {data.drift.key_factors.map((f) => (
                  <li key={f}>{f}</li>
                ))}
              </ul>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Cost Optimization
            </CardTitle>
            <CardDescription>
              Potential savings: ${data.cost.estimated_annual_savings.toLocaleString()}/yr
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <AiInsightBox text={data.cost.ai_insight} />
            <ReportBarChart data={data.cost.cost_distribution} valueLabel="TCO ratio %" color="#f59e0b" />
            <ReportBarChart
              data={data.cost.department_costs}
              valueLabel="Maintenance spend"
              color="#0ea5e9"
              height={180}
            />
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Replacement Planning
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <AiInsightBox text={data.replacement.ai_insight} />
            {data.replacement.items.length ? (
              <div className="grid gap-3 md:grid-cols-2">
                {data.replacement.items.map((item) => (
                  <div key={item.asset_id} className="rounded-lg border p-4 text-sm">
                    <Link to={`/assets/${item.asset_id}`} className="font-semibold text-primary hover:underline">
                      {item.asset_tag} — {item.asset_name}
                    </Link>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {item.priority} · {item.remaining_useful_life_months} mo remaining · Health trend:{" "}
                      {item.health_trend}
                    </p>
                    <p className="mt-2">{item.why_replace}</p>
                    <p className="mt-2 text-muted-foreground">{item.repair_vs_replace}</p>
                    <p className="mt-1 text-amber-800">{item.business_impact_if_delayed}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No replacement candidates in scope.</p>
            )}
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Maintenance Schedule
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <AiInsightBox text={data.maintenance.ai_insight} />
            <p className="text-sm text-muted-foreground">{data.maintenance.skip_risk_summary}</p>
            <div className="grid gap-4 md:grid-cols-2">
              <ReportBarChart
                data={data.maintenance.priority_ranking}
                valueLabel="Days until service"
                color="#10b981"
              />
              <ReportBarChart
                data={data.maintenance.department_workload}
                valueLabel="Scheduled items"
                color="#6366f1"
              />
            </div>
            {data.maintenance.items.length ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Asset</TableHead>
                    <TableHead>Window</TableHead>
                    <TableHead>Days</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.maintenance.items.map((item) => (
                    <TableRow key={item.asset_id}>
                      <TableCell>
                        <Link to={`/assets/${item.asset_id}`} className="font-medium text-primary hover:underline">
                          {item.asset_tag}
                        </Link>
                        <p className="text-xs text-muted-foreground">{item.rationale}</p>
                      </TableCell>
                      <TableCell>{item.suggested_window}</TableCell>
                      <TableCell>{item.suggested_within_days}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
