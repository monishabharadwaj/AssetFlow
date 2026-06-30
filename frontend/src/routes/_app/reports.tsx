import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { FileText, BarChart3, Printer } from "lucide-react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
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
import type { OperationsReport, ReportSection } from "@/lib/types/ui";
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
          <p className="font-medium">Loading executive brief…</p>
          <p className="mt-1 text-xs text-muted-foreground">Analytics below; narrative will update when ready.</p>
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
          showEnhanced={showEnhanced}
          isEnhancing={isEnhancing}
          user={user}
        />
      )}
    </div>
  );
}

function ReportMetrics({ metrics }: { metrics: OperationsReport["metrics"] }) {
  if (!metrics?.length) return null;
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {metrics.slice(0, 6).map((m) => (
        <div key={m.label} className={cn(glassCardClass(), "p-3")}>
          <div className="text-[10px] uppercase tracking-wider text-muted-foreground">{m.label}</div>
          <div className="text-xl font-semibold mt-1 tabular-nums">{m.value}</div>
        </div>
      ))}
    </div>
  );
}

function ReportAnalyticsCharts({
  charts,
  user,
  condensed = false,
}: {
  charts: NonNullable<OperationsReport["standard_charts"]>;
  user: ReturnType<typeof useAuth>["user"];
  condensed?: boolean;
}) {
  const declining = (
    <ChartCard
      title="Assets with declining health"
      subtitle="Health delta % per asset"
      data={charts.health_trend_chart}
      emptyTitle="No deteriorating assets"
      emptyHint="No meaningful health decline detected."
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
  );

  const priority = (
    <ChartCard
      title="Maintenance priority ranking"
      subtitle="Highest-priority work by asset"
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
  );

  if (condensed) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {declining}
        {priority}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 print:break-inside-avoid">
      {declining}
      {priority}
      {user?.role === "ADMIN" && (charts.department_comparison?.length ?? 0) > 0 && (
        <ChartCard title="Avg health by department" subtitle="Organization comparison" data={charts.department_comparison} heightClass="h-56">
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

function MetricBar({ value, critical }: { value: number; critical?: boolean }) {
  const pct = Math.min(100, Math.max(0, value));
  return (
    <div className="flex items-center gap-2 min-w-[5.5rem]">
      <div className="flex-1 h-1.5 rounded-full bg-muted/50 overflow-hidden">
        <div
          className={cn("h-full rounded-full", critical ? "bg-critical" : "bg-primary/70")}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={cn("text-xs tabular-nums shrink-0", critical && "text-critical")}>{pct}%</span>
    </div>
  );
}

function countDivergentReplacements(
  rows: NonNullable<OperationsReport["appendices"]>["replacement_planning"],
): number {
  if (!rows?.length) return 0;
  return rows.filter((r) => r.lifeRemainingPct > 60 && r.healthPct != null && r.healthPct < 45).length;
}

function isAssetTagBullet(text: string): boolean {
  return /^[A-Z]{2,5}-[A-Z]{2,6}-\d{3,5}/.test(text.trim());
}

function DeptMicroBars({ data }: { data: { label: string; value: number }[] }) {
  if (!data.length) return null;
  const max = Math.max(...data.map((d) => d.value), 1);
  return (
    <div className="mt-3 space-y-2">
      {data.slice(0, 5).map((d) => (
        <div key={d.label} className="space-y-1">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground truncate pr-2">{d.label}</span>
            <span className="tabular-nums font-medium">{d.value}%</span>
          </div>
          <div className="h-1.5 rounded-full bg-muted/50 overflow-hidden">
            <div
              className="h-full rounded-full bg-[oklch(0.7_0.16_240)]"
              style={{ width: `${Math.round((d.value / max) * 100)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

function NarrativeSectionCard({
  section,
  index,
  deptChartData,
  enhanced,
}: {
  section: ReportSection;
  index: number;
  deptChartData?: { label: string; value: number }[];
  enhanced?: boolean;
}) {
  const isDept = section.title.toLowerCase().includes("department");
  const isAiObs = section.title.toLowerCase().includes("ai observation");
  const isRisk = section.title.toLowerCase().includes("risk") || section.title.toLowerCase().includes("immediate attention");

  return (
    <Card
      className={cn(
        glassCardClass(),
        "p-4 print:break-inside-avoid",
        isAiObs && enhanced && "border-l-2 border-l-[oklch(0.65_0.22_285)]",
      )}
    >
      <div className="flex items-baseline gap-2">
        <span className="text-lg font-light text-muted-foreground tabular-nums">
          {String(section.number ?? index + 1).padStart(2, "0")}
        </span>
        <h4 className="text-base font-semibold">{section.title}</h4>
      </div>
      <div className="mt-2 space-y-2 pl-6">
        {section.paragraphs?.map((p, j) => (
          <p key={j} className="text-sm leading-relaxed text-foreground/85">{p}</p>
        ))}
        {isDept && deptChartData && deptChartData.length > 0 ? (
          <DeptMicroBars data={deptChartData} />
        ) : section.bullets && section.bullets.length > 0 ? (
          isRisk ? (
            <div className="flex flex-wrap gap-1.5">
              {section.bullets.map((b, j) =>
                isAssetTagBullet(b) ? (
                  <Pill key={j} tone={priorityTone.HIGH} className="font-mono text-[10px]">
                    {b.split(/\s/)[0]}
                  </Pill>
                ) : (
                  <span key={j} className="text-sm text-foreground/85 block w-full">{b}</span>
                ),
              )}
            </div>
          ) : (
            <ul className="text-sm leading-relaxed text-foreground/85 list-disc list-inside space-y-1 marker:text-muted-foreground">
              {section.bullets.map((b, j) => <li key={j}>{b}</li>)}
            </ul>
          )
        ) : null}
      </div>
    </Card>
  );
}

function ReportHeader({
  scopeLabel,
  generatedAt,
  showEnhanced,
  isAiEnhanced,
}: {
  scopeLabel: string;
  generatedAt: string;
  showEnhanced: boolean;
  isAiEnhanced: boolean;
}) {
  return (
    <Card
      className={cn(
        glassCardClass(),
        "p-6 print:shadow-none",
        showEnhanced && "border-t-2 border-t-[oklch(0.65_0.22_285)]/60 bg-gradient-to-br from-[oklch(0.22_0.04_285)]/40 to-transparent",
      )}
    >
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <div className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">
            {showEnhanced ? "Executive brief" : "Operations & Fleet Report"}
          </div>
          <h2 className="text-2xl font-semibold mt-2">{scopeLabel}</h2>
          <p className="text-sm text-muted-foreground mt-1">Generated {fmtDate(generatedAt)}</p>
        </div>
        <div className="flex items-center gap-2">
          {showEnhanced && (
            <Pill className="text-[10px]">
              {isAiEnhanced ? "Enhanced by AI" : "Executive template"}
            </Pill>
          )}
          <div className="size-12 rounded-xl bg-primary/15 grid place-items-center text-[oklch(0.82_0.18_285)]">
            <FileText className="size-6" />
          </div>
        </div>
      </div>
    </Card>
  );
}

function StandardReportLayout({
  report,
  user,
}: {
  report: OperationsReport;
  user: ReturnType<typeof useAuth>["user"];
}) {
  const charts = report.standard_charts;
  return (
    <div className="space-y-6">
      <ReportMetrics metrics={report.metrics} />
      {charts && (
        <>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Analytics</h3>
          <ReportAnalyticsCharts charts={charts} user={user} />
        </>
      )}
      {report.text_summaries && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {report.text_summaries.drift && (
            <Card className={cn(glassCardClass(), "p-4")}>
              <CardHeader title="Health drift insight" />
              <p className="text-sm leading-relaxed mt-1 text-foreground/85">{report.text_summaries.drift}</p>
            </Card>
          )}
          {report.text_summaries.maintenance && (
            <Card className={cn(glassCardClass(), "p-4")}>
              <CardHeader title="Maintenance insight" />
              <p className="text-sm leading-relaxed mt-1 text-foreground/85">{report.text_summaries.maintenance}</p>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}

function EnhancedReportLayout({
  narrativeReport,
  standardReport,
  isEnhancing,
  user,
}: {
  narrativeReport: OperationsReport;
  standardReport: OperationsReport;
  isEnhancing?: boolean;
  user: ReturnType<typeof useAuth>["user"];
}) {
  const sections = narrativeReport.sections;
  const heroSections = sections.slice(0, 2);
  const gridSections = sections.slice(2);
  const actionsSection = sections.find((s) => s.title.toLowerCase().includes("recommended action"));
  const charts = standardReport.standard_charts;
  const deptData = charts?.department_comparison ?? [];
  const replacementRows = narrativeReport.appendices?.replacement_planning;
  const divergenceCount = countDivergentReplacements(replacementRows);

  if (isEnhancing) {
    return (
      <div className="space-y-3">
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-56 w-full" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <ReportMetrics metrics={standardReport.metrics} />

      {divergenceCount > 0 && (
        <div className="rounded-lg border border-[oklch(0.65_0.22_285)]/35 bg-[oklch(0.22_0.04_285)]/30 px-4 py-3">
          <div className="text-[10px] uppercase tracking-wider text-[oklch(0.78_0.16_285)]">Key finding</div>
          <p className="text-sm mt-1 text-foreground/90">
            {divergenceCount} asset{divergenceCount !== 1 ? "s are" : " is"} chronologically young but operationally
            critical — accelerated capital review recommended.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          {heroSections.map((s, i) => (
            <Card key={i} className={cn(glassCardClass(), "p-5")}>
              <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1">
                {String(s.number ?? i + 1).padStart(2, "0")}
              </div>
              <h3 className="text-lg font-semibold">{s.title}</h3>
              {s.paragraphs?.map((p, j) => (
                <p key={j} className="text-sm leading-relaxed text-foreground/90 mt-2">{p}</p>
              ))}
              {s.bullets && s.bullets.length > 0 && (
                <ul className="mt-3 text-sm space-y-1 text-foreground/85 list-disc list-inside">
                  {s.bullets.slice(0, 3).map((b, j) => <li key={j}>{b}</li>)}
                </ul>
              )}
            </Card>
          ))}
        </div>
        {actionsSection && (
          <Card className={cn(glassCardClass(), "p-5 border border-[oklch(0.65_0.22_285)]/25")}>
            <div className="text-[10px] uppercase tracking-wider text-[oklch(0.78_0.16_285)]">Actions this week</div>
            <h3 className="text-base font-semibold mt-2">{actionsSection.title}</h3>
            <p className="text-sm text-muted-foreground mt-2">{actionsSection.paragraphs?.[0]}</p>
            <ul className="mt-4 space-y-2">
              {actionsSection.bullets?.slice(0, 5).map((b, j) => (
                <li key={j} className="text-sm flex gap-2">
                  <span className="text-[oklch(0.78_0.16_285)]">→</span>
                  <span>{b}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}
      </div>

      {charts && (
        <>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Key analytics</h3>
          <ReportAnalyticsCharts charts={charts} user={user} condensed />
        </>
      )}

      <div>
        <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Detailed findings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {gridSections.map((s, i) => (
            <NarrativeSectionCard
              key={i}
              section={s}
              index={i + 2}
              deptChartData={s.title.toLowerCase().includes("department") ? deptData : undefined}
              enhanced
            />
          ))}
        </div>
      </div>

      {narrativeReport.text_summaries?.cost && (
        <Card className={cn(glassCardClass(), "p-4")}>
          <CardHeader title="Cost optimization" />
          <p className="text-sm leading-relaxed mt-1">{narrativeReport.text_summaries.cost}</p>
        </Card>
      )}

      {narrativeReport.appendices && (
        <section className="space-y-4 pt-4 border-t border-border print:break-before-page">
          <div>
            <div className="text-[11px] uppercase tracking-[0.2em] text-muted-foreground">Operational schedules</div>
            <h3 className="text-xl font-semibold mt-1">Maintenance & replacement planning</h3>
          </div>

          {narrativeReport.appendices.maintenance_schedule && narrativeReport.appendices.maintenance_schedule.length > 0 && (
            <Card className={cn(glassCardClass(), "p-0 overflow-hidden")}>
              <div className="p-4"><CardHeader title="Maintenance schedule" subtitle="Suggested service windows by priority" /></div>
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground border-t border-border">
                    <th className="px-4 py-2">Tag</th>
                    <th className="px-4 py-2">Name</th>
                    <th className="px-4 py-2">Window</th>
                    <th className="px-4 py-2">Priority</th>
                  </tr>
                </thead>
                <tbody>
                  {narrativeReport.appendices.maintenance_schedule.map((m, i) => (
                    <tr key={i} className="border-t border-border">
                      <td className="px-4 py-2 font-mono text-xs">{m.asset_tag}</td>
                      <td className="px-4 py-2">{m.name}</td>
                      <td className="px-4 py-2 text-muted-foreground">{m.dueWindow ?? "—"}</td>
                      <td className="px-4 py-2"><Pill tone={priorityTone[m.priority]}>{m.priority}</Pill></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          )}

          {replacementRows && replacementRows.length > 0 && (
            <Card className={cn(glassCardClass(), "p-0 overflow-hidden")}>
              <div className="p-4">
                <CardHeader
                  title="Capital & lifecycle"
                  subtitle="Replacement candidates ranked by urgency"
                />
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm min-w-[720px]">
                  <thead>
                    <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground border-t border-border">
                      <th className="px-4 py-2">Tag</th>
                      <th className="px-4 py-2">Name</th>
                      <th className="px-4 py-2">Priority</th>
                      <th className="px-4 py-2">Health</th>
                      <th className="px-4 py-2">Life left</th>
                      <th className="px-4 py-2">Window</th>
                      <th className="px-4 py-2">Rationale</th>
                    </tr>
                  </thead>
                  <tbody>
                    {replacementRows.slice(0, 10).map((r, i) => (
                      <tr key={i} className="border-t border-border align-top">
                        <td className="px-4 py-2 font-mono text-xs">{r.asset_tag}</td>
                        <td className="px-4 py-2 max-w-[8rem] truncate">{r.name}</td>
                        <td className="px-4 py-2">
                          <Pill tone={priorityTone[r.priority]}>{r.priority}</Pill>
                        </td>
                        <td className="px-4 py-2">
                          {r.healthPct != null ? (
                            <MetricBar value={r.healthPct} critical={r.healthPct < 45} />
                          ) : (
                            "—"
                          )}
                        </td>
                        <td className="px-4 py-2">
                          <MetricBar value={Math.round(r.lifeRemainingPct)} />
                        </td>
                        <td className="px-4 py-2 text-muted-foreground whitespace-nowrap">{r.recommendedWindow}</td>
                        <td
                          className="px-4 py-2 text-muted-foreground text-xs max-w-xs line-clamp-2"
                          title={r.reason ?? undefined}
                        >
                          {r.reason ?? "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </section>
      )}
    </div>
  );
}

function ReportDocument({
  standardReport,
  narrativeReport,
  showEnhanced,
  isEnhancing,
  user,
}: {
  standardReport: OperationsReport;
  narrativeReport: OperationsReport;
  showEnhanced: boolean;
  isEnhancing?: boolean;
  user: ReturnType<typeof useAuth>["user"];
}) {
  const scopeLabel = formatScopeLabel(standardReport.scope, user);
  const isAiEnhanced = narrativeReport.source === "ollama" || narrativeReport.source === "enhanced_template";

  return (
    <div className="space-y-6">
      <ReportHeader
        scopeLabel={scopeLabel}
        generatedAt={standardReport.generated_at}
        showEnhanced={showEnhanced}
        isAiEnhanced={isAiEnhanced}
      />

      {showEnhanced ? (
        <EnhancedReportLayout
          narrativeReport={narrativeReport}
          standardReport={standardReport}
          isEnhancing={isEnhancing}
          user={user}
        />
      ) : (
        <StandardReportLayout report={standardReport} user={user} />
      )}
    </div>
  );
}
