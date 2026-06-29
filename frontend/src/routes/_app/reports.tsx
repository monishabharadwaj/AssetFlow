import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { FileText, BarChart3, Printer } from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, LineChart, Line,
} from "recharts";

import { Card, CardHeader, Pill, Skeleton, EmptyState } from "@/components/ui-bits";
import { ChartCard } from "@/features/dashboard/components/chart-card";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import { usePermissions } from "@/features/auth/use-permissions";
import { useReportsAnalytics } from "@/features/operations/hooks";
import { useAuth } from "@/lib/auth-context";
import { chartTooltipStyle } from "@/lib/chart-theme";
import { formatScopeLabel } from "@/lib/format-scope";
import { guardRoute } from "@/lib/route-guards";
import type { OperationsReport } from "@/lib/types/ui";
import { fmtDate, priorityTone } from "@/lib/format";
import { toast } from "@/lib/toast";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/_app/reports")({
  beforeLoad: () => guardRoute("/reports"),
  component: ReportsPage,
});

const tooltipStyle = chartTooltipStyle;

function ReportsPage() {
  const { user } = useAuth();
  const { can } = usePermissions();
  const canToggle = can("intelligence:run");
  const [enhanced, setEnhanced] = useState(false);
  const showEnhanced = canToggle && enhanced;

  const templateQuery = useReportsAnalytics(false, true);
  const enhancedQuery = useReportsAnalytics(true, showEnhanced);

  const standardReport = templateQuery.data;
  const enhancedReport = enhancedQuery.data;
  const narrativeReport = showEnhanced && enhancedReport ? enhancedReport : standardReport;
  const isLoading = templateQuery.isLoading && !standardReport;
  const isEnhancing = showEnhanced && enhancedQuery.isFetching && !enhancedReport;
  const enhancedToastShown = useRef(false);

  useEffect(() => {
    if (!showEnhanced) {
      enhancedToastShown.current = false;
      return;
    }
    if (enhancedQuery.isError) {
      toast("Enhanced analysis unavailable — is Ollama running?", "error");
      return;
    }
    if (enhancedReport && !enhancedQuery.isFetching && !enhancedToastShown.current) {
      enhancedToastShown.current = true;
      if (enhancedReport.source !== "ollama" && enhancedReport.source !== "enhanced_template") {
        toast("Using standard narrative; AI enhancement did not apply.");
      }
    }
  }, [showEnhanced, enhancedQuery.isError, enhancedQuery.isFetching, enhancedReport]);

  return (
    <div className="space-y-6 print:space-y-4">
      <div className="flex flex-wrap items-end justify-between gap-3 print:hidden">
        <div>
          <h1 className="text-2xl font-semibold">Reports</h1>
          <p className="text-sm text-muted-foreground mt-1">Operations & fleet reporting</p>
        </div>
        <div className="flex items-center gap-2">
          {canToggle && (
            <label className="flex items-center gap-2 h-9 px-3 rounded-lg border border-border text-sm cursor-pointer">
              <input
                type="checkbox"
                checked={enhanced}
                onChange={(e) => setEnhanced(e.target.checked)}
                className="accent-[oklch(0.65_0.22_285)]"
              />
              <BarChart3 className="size-4 text-muted-foreground" />
              Enhanced analysis
            </label>
          )}
          <button type="button" onClick={() => window.print()} className="h-9 px-3 rounded-lg border border-border hover:bg-accent/40 text-sm flex items-center gap-2">
            <Printer className="size-4" /> Print
          </button>
        </div>
      </div>

      {isEnhancing ? (
        <div className="rounded-lg border bg-muted/40 p-3 text-sm print:hidden">
          <p className="font-medium">Loading enhanced analysis…</p>
          <p className="mt-1 text-xs text-muted-foreground">Standard report shown below; charts will appear when ready.</p>
        </div>
      ) : null}

      {isLoading ? (
        <div className="space-y-3"><Skeleton className="h-32" /><Skeleton className="h-48" /><Skeleton className="h-48" /></div>
      ) : templateQuery.isError || !standardReport ? (
        <Card><EmptyState title="Couldn't load report" hint={(templateQuery.error as Error | undefined)?.message ?? "Try again later."} icon={<FileText className="size-5" />} /></Card>
      ) : (
        <ReportDocument
          standardReport={standardReport}
          narrativeReport={narrativeReport ?? standardReport}
          showAppendices={showEnhanced}
          isEnhancing={isEnhancing}
          user={user}
        />
      )}
    </div>
  );
}

function ReportAnalyticsCharts({
  charts,
  user,
}: {
  charts: NonNullable<OperationsReport["standard_charts"]>;
  user: ReturnType<typeof useAuth>["user"];
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 print:break-inside-avoid">
      <ChartCard
        title="Assets with declining health"
        subtitle="Health delta % per asset (not a time series)"
        data={charts.health_trend_chart}
        emptyTitle="No deteriorating assets"
        emptyHint="No meaningful health decline detected in the current scoring window."
        heightClass="h-56"
      >
        <ResponsiveContainer>
          <BarChart data={(charts.health_trend_chart ?? []).map((p) => ({ name: p.label, value: p.value }))} layout="vertical">
            <CartesianGrid stroke="rgba(255,255,255,0.05)" horizontal={false} />
            <XAxis type="number" tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="name" width={88} tick={{ fill: "rgb(160,160,180)", fontSize: 9 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={tooltipStyle} />
            <Bar dataKey="value" fill="oklch(0.78 0.22 18)" radius={[0, 4, 4, 0]} maxBarSize={20} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard
        title="Maintenance priority ranking"
        subtitle="Highest-priority work items by asset"
        data={charts.priority_ranking}
        emptyTitle="No maintenance priorities"
        emptyHint="Run Refresh analysis on the Operations Center."
        heightClass="h-56"
      >
        <ResponsiveContainer>
          <BarChart data={(charts.priority_ranking ?? []).map((p) => ({ name: p.label, value: p.value }))} layout="vertical">
            <CartesianGrid stroke="rgba(255,255,255,0.05)" horizontal={false} />
            <XAxis type="number" tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="name" width={88} tick={{ fill: "rgb(160,160,180)", fontSize: 9 }} axisLine={false} tickLine={false} />
            <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
            <Bar dataKey="value" fill="oklch(0.78 0.15 75)" radius={[0, 4, 4, 0]} maxBarSize={20} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {user?.role === "ADMIN" && (charts.department_comparison?.length ?? 0) > 0 && (
        <ChartCard
          title="Avg health by department"
          subtitle="Organization comparison"
          data={charts.department_comparison}
          emptyHint="No department comparison data."
          heightClass="h-56"
        >
          <ResponsiveContainer>
            <BarChart data={(charts.department_comparison ?? []).map((p) => ({ name: p.label, value: p.value }))}>
              <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
              <Bar dataKey="value" fill="oklch(0.7 0.16 240)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      )}

      {(charts.department_workload?.length ?? 0) > 0 && (
        <ChartCard
          title="Maintenance workload by department"
          subtitle={user?.role === "ADMIN" ? "Open work across departments" : "Your department queue"}
          data={charts.department_workload}
          emptyHint="No workload data."
          heightClass="h-56"
        >
          <ResponsiveContainer>
            <BarChart data={(charts.department_workload ?? []).map((p) => ({ name: p.label, value: p.value }))}>
              <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="name" tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "rgb(160,160,180)", fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} cursor={{ fill: "rgba(255,255,255,0.03)" }} />
              <Bar dataKey="value" fill="oklch(0.72 0.17 155)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      )}
    </div>
  );
}

function ReportDocument({
  standardReport,
  narrativeReport,
  showAppendices,
  isEnhancing,
  user,
}: {
  standardReport: OperationsReport;
  narrativeReport: OperationsReport;
  showAppendices: boolean;
  isEnhancing?: boolean;
  user: ReturnType<typeof useAuth>["user"];
}) {
  const scopeLabel = formatScopeLabel(standardReport.scope, user);
  const charts = standardReport.standard_charts;
  const isAiEnhanced = narrativeReport.source === "ollama" || narrativeReport.source === "enhanced_template";

  return (
    <div className="space-y-6">
      <Card className={cn(glassCardClass(), "p-6 print:shadow-none")}>
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <div className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">Operations & Fleet Report</div>
            <h2 className="text-2xl font-semibold mt-2">{scopeLabel}</h2>
            <p className="text-sm text-muted-foreground mt-1">Generated {fmtDate(standardReport.generated_at)}</p>
          </div>
          <div className="flex items-center gap-2">
            {showAppendices && (
              <Pill className="text-[10px]">
                {isAiEnhanced ? "Enhanced by AI" : "Standard report"}
              </Pill>
            )}
            <div className="size-12 rounded-xl bg-primary/15 grid place-items-center text-[oklch(0.82_0.18_285)]">
              <FileText className="size-6" />
            </div>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 print:block">
        <div className="lg:col-span-3 space-y-4 print:mb-6">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground print:hidden">Analytics</h3>
          {standardReport.metrics?.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {standardReport.metrics.slice(0, 6).map((m) => (
                <div key={m.label} className={cn(glassCardClass(), "p-3")}>
                  <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{m.label}</div>
                  <div className="text-xl font-semibold mt-1 tabular-nums">{m.value}</div>
                </div>
              ))}
            </div>
          )}
          {charts && <ReportAnalyticsCharts charts={charts} user={user} />}
          {standardReport.text_summaries && !showAppendices && (
            <div className="space-y-3">
              {standardReport.text_summaries.drift && (
                <Card className={cn(glassCardClass(), "p-4")}>
                  <CardHeader title="Health drift insight" />
                  <p className="text-sm leading-relaxed mt-1 text-foreground/85">{standardReport.text_summaries.drift}</p>
                </Card>
              )}
              {standardReport.text_summaries.maintenance && (
                <Card className={cn(glassCardClass(), "p-4")}>
                  <CardHeader title="Maintenance insight" />
                  <p className="text-sm leading-relaxed mt-1 text-foreground/85">{standardReport.text_summaries.maintenance}</p>
                </Card>
              )}
            </div>
          )}
        </div>

        <div className="lg:col-span-2 space-y-3 print:mt-4">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground print:hidden">Executive summary</h3>
          {isEnhancing ? (
            <div className="space-y-3">
              <Skeleton className="h-28 w-full" />
              <Skeleton className="h-28 w-full" />
              <Skeleton className="h-28 w-full" />
              <Skeleton className="h-28 w-full" />
            </div>
          ) : (
            <>
              {narrativeReport.sections.map((s, i) => (
                <Card key={i} className={cn(glassCardClass(), "p-4 print:break-inside-avoid")}>
                  <div className="flex items-baseline gap-2">
                    <span className="text-lg font-light text-muted-foreground tabular-nums">{String(s.number ?? i + 1).padStart(2, "0")}</span>
                    <h4 className="text-base font-semibold">{s.title}</h4>
                  </div>
                  <div className="mt-2 space-y-2 pl-6">
                    {s.paragraphs?.map((p, j) => (
                      <p key={j} className="text-sm leading-relaxed text-foreground/85">{p}</p>
                    ))}
                    {s.bullets && s.bullets.length > 0 && (
                      <ul className="text-sm leading-relaxed text-foreground/85 list-disc list-inside space-y-1 marker:text-muted-foreground">
                        {s.bullets.map((b, j) => <li key={j}>{b}</li>)}
                      </ul>
                    )}
                  </div>
                </Card>
              ))}
              {narrativeReport.text_summaries?.cost && (
                <Card className={cn(glassCardClass(), "p-4")}>
                  <CardHeader title="Cost optimization" />
                  <p className="text-sm leading-relaxed mt-1">{narrativeReport.text_summaries.cost}</p>
                </Card>
              )}
              {showAppendices && narrativeReport.text_summaries && (
                <div className="space-y-3">
                  {narrativeReport.text_summaries.drift && (
                    <Card className={cn(glassCardClass(), "p-4")}>
                      <CardHeader title="Health drift insight" />
                      <p className="text-sm leading-relaxed mt-1 text-foreground/85">{narrativeReport.text_summaries.drift}</p>
                    </Card>
                  )}
                  {narrativeReport.text_summaries.maintenance && (
                    <Card className={cn(glassCardClass(), "p-4")}>
                      <CardHeader title="Maintenance insight" />
                      <p className="text-sm leading-relaxed mt-1 text-foreground/85">{narrativeReport.text_summaries.maintenance}</p>
                    </Card>
                  )}
                  {narrativeReport.text_summaries.replacement && (
                    <Card className={cn(glassCardClass(), "p-4")}>
                      <CardHeader title="Replacement planning" />
                      <p className="text-sm leading-relaxed mt-1 text-foreground/85">{narrativeReport.text_summaries.replacement}</p>
                    </Card>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {showAppendices && narrativeReport.appendices && (
        <section className="space-y-4 pt-4 border-t border-border print:break-before-page">
          <div>
            <div className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">Appendices</div>
            <h3 className="text-xl font-semibold mt-1">Enhanced visual analytics</h3>
          </div>
          {narrativeReport.appendices.benchmarks && narrativeReport.appendices.benchmarks.length > 0 && (
            <Card className={glassCardClass()}>
              <CardHeader title="Benchmark KPIs" subtitle="Department vs company" />
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {narrativeReport.appendices.benchmarks.map((b) => (
                  <div key={b.label} className="rounded-lg border border-border/80 p-4">
                    <div className="text-xs text-muted-foreground">{b.label}</div>
                    <div className="text-2xl font-semibold mt-1 tabular-nums">{b.value}</div>
                  </div>
                ))}
              </div>
            </Card>
          )}
          {narrativeReport.appendices.health_drift && narrativeReport.appendices.health_drift.length > 0 && (
            <ChartCard title="Health drift" subtitle="Current vs previous period" data={narrativeReport.appendices.health_drift} heightClass="h-64">
              <ResponsiveContainer>
                <LineChart data={narrativeReport.appendices.health_drift}>
                  <CartesianGrid stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="name" tick={{ fill: "rgb(160,160,180)", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: "rgb(160,160,180)", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Line type="monotone" dataKey="previous" stroke="rgba(255,255,255,0.35)" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="current" stroke="oklch(0.7 0.22 285)" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
          )}
          {narrativeReport.appendices.maintenance_schedule && narrativeReport.appendices.maintenance_schedule.length > 0 && (
            <Card className={cn(glassCardClass(), "p-0 overflow-hidden")}>
              <div className="p-4"><CardHeader title="Maintenance schedule" subtitle="Upcoming by priority" /></div>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground border-t border-border">
                    <th className="px-4 py-2">Tag</th>
                    <th className="px-4 py-2">Name</th>
                    <th className="px-4 py-2">Due</th>
                    <th className="px-4 py-2">Priority</th>
                  </tr>
                </thead>
                <tbody>
                  {narrativeReport.appendices.maintenance_schedule.map((m, i) => (
                    <tr key={i} className="border-t border-border">
                      <td className="px-4 py-2 font-mono text-xs">{m.asset_tag}</td>
                      <td className="px-4 py-2">{m.name}</td>
                      <td className="px-4 py-2 text-muted-foreground">{fmtDate(m.due)}</td>
                      <td className="px-4 py-2"><Pill tone={priorityTone[m.priority]}>{m.priority}</Pill></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          )}
        </section>
      )}
    </div>
  );
}
