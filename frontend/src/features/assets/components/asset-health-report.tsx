import type {
  EnterpriseHealthBrief,
  ExplanationFactor,
  HealthPrediction,
  RootCauseResponse,
} from "../../intelligence/api/intelligence-api";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../../../shared/components/ui/card";
import { Skeleton } from "../../../shared/components/ui/skeleton";
import {
  healthBandFromPct,
  HEALTH_BAND_TEXT,
  type HealthBand,
} from "../../../shared/lib/ops-semantics";
import { cn } from "../../../shared/lib/utils";

type AssetHealthReportProps = {
  assetName: string;
  prediction: HealthPrediction | null;
  explanationSummary: string | null;
  enterpriseBrief: EnterpriseHealthBrief | null;
  rootCause: RootCauseResponse | null;
  isExplainLoading: boolean;
  factors: ExplanationFactor[];
  onExplain: () => void;
};

function bandBadgeClass(band: HealthBand) {
  return HEALTH_BAND_TEXT[band];
}

export function AssetHealthReport({
  assetName,
  prediction,
  explanationSummary,
  enterpriseBrief,
  rootCause,
  isExplainLoading,
  factors,
  onExplain,
}: AssetHealthReportProps) {
  const brief = rootCause?.enterprise_brief ?? enterpriseBrief;
  const healthPct = prediction
    ? Math.round(prediction.health_score * 100)
    : null;
  const band = healthPct != null ? healthBandFromPct(healthPct) : null;

  if (!prediction && !explanationSummary) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-sm text-muted-foreground">
          Run an AI assessment to generate a health report for {assetName}.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card
        className={cn(
          "rounded-3xl border border-slate-700 bg-[#111827] shadow-[0_0_25px_rgba(59,130,246,0.12)]",
          brief?.is_improvement && "border-emerald-500/40",
        )}
      >
        <CardHeader className="pb-2">
          <CardTitle className="text-xl font-bold text-white">
            AI health report
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-end gap-6">
            {healthPct != null ? (
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Overall health
                </p>
                <p
                  className={cn(
                    "text-5xl font-semibold tabular-nums",
                    band && bandBadgeClass(band),
                  )}
                >
                  {healthPct}%
                </p>
                {band ? (
                  <p
                    className={cn("text-sm font-medium", bandBadgeClass(band))}
                  >
                    {brief?.health_band ?? band}
                  </p>
                ) : null}
              </div>
            ) : null}
            {prediction ? (
              <div className="space-y-1 text-sm">
                <p>
                  <span className="text-muted-foreground">Confidence: </span>
                  {brief?.confidence_label ??
                    `${Math.round(prediction.confidence * 100)}%`}
                </p>
                {brief?.remaining_useful_life ? (
                  <p>
                    <span className="text-muted-foreground">
                      Est. useful life:{" "}
                    </span>
                    {brief.remaining_useful_life}
                  </p>
                ) : null}
                {brief?.priority ? (
                  <p>
                    <span className="text-muted-foreground">Priority: </span>
                    <span className="font-medium">{brief.priority}</span>
                  </p>
                ) : null}
              </div>
            ) : null}
          </div>

          {brief ? (
            <div className="grid gap-4 md:grid-cols-2">
              <ReportSection title="What happened" body={brief.what_happened} />
              <ReportSection
                title="Why we flagged this"
                body={brief.why_predicted}
              />
              <ReportSection
                title="Business impact"
                body={brief.business_impact}
              />
              <ReportSection
                title="Recommended action"
                body={brief.recommended_action}
                highlight
              />
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              {explanationSummary}
            </p>
          )}

          {(brief || isExplainLoading) && (
            <div className="grid gap-3 rounded-2xl border border-slate-700 bg-slate-900/60 p-4 sm:grid-cols-3">
              <MiniStat
                label="Est. downtime"
                value={brief?.estimated_downtime ?? "—"}
              />
              <MiniStat
                label="Est. effort"
                value={brief?.estimated_effort ?? "—"}
              />
              <MiniStat
                label="Est. cost"
                value={brief?.estimated_cost ?? "—"}
              />
            </div>
          )}

          {factors.length > 0 ? (
            <div>
              <p className="mb-2 text-xs font-medium uppercase tracking-wide text-slate-400">
                Contributing factors
              </p>
              <ul className="space-y-1.5">
                {factors.slice(0, 5).map((f) => (
                  <li
                    key={f.factor}
                    className="flex gap-2 text-sm text-muted-foreground"
                  >
                    <span className="text-foreground">•</span>
                    {f.message}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}

          <div>
            <button
              type="button"
              className="text-sm font-medium text-primary hover:underline disabled:opacity-50"
              disabled={isExplainLoading}
              onClick={onExplain}
            >
              {isExplainLoading
                ? "Generating detailed brief…"
                : "Refresh detailed explanation"}
            </button>
            {isExplainLoading ? (
              <div className="mt-3 space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <Skeleton className="h-4 w-4/6" />
              </div>
            ) : rootCause?.root_cause_summary &&
              rootCause.source === "ollama" ? (
              <p className="mt-3 rounded-2xl border border-slate-700 bg-slate-900/60 p-4 text-sm leading-relaxed">
                {rootCause.root_cause_summary}
              </p>
            ) : null}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function ReportSection({
  title,
  body,
  highlight,
}: {
  title: string;
  body: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={cn(
        "rounded-2xl border border-slate-700 bg-slate-900/60 p-4",
        highlight && "border-blue-500/40 bg-blue-500/10",
      )}
    >
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {title}
      </p>
      <p className="mt-1 text-sm leading-relaxed">{body}</p>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm font-medium">{value}</p>
    </div>
  );
}
