import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, EmptyState, Pill, Skeleton } from "@/components/ui-bits";
import { AssetTypeVisual } from "@/features/assets/components/asset-type-visual";
import { AssetHealthTrendChart } from "@/features/assets/components/asset-health-trend-chart";import { usePermissions } from "@/features/auth/use-permissions";
import {
  fetchAssetRecommendations,
  fetchAssetRootCause,
  predictAssetHealth,
} from "@/features/intelligence/api";
import { pct, priorityTone } from "@/lib/format";
import { toast } from "@/lib/toast";
import type { EnterpriseHealthBrief, ExplanationFactor, HealthPredictionResponse, RootCauseResponse } from "@/lib/types/backend";
import type { Priority } from "@/lib/types/ui";

type Props = {
  assetId: string;
  assetTypeName?: string | null;
  assetName?: string | null;
};

function riskPriority(risk: string): Priority {
  const u = risk.toUpperCase();
  if (u === "HIGH") return "HIGH";
  if (u === "MEDIUM") return "MEDIUM";
  return "LOW";
}

export function AssetHealthAnalysis({ assetId, assetTypeName, assetName }: Props) {
  const { can } = usePermissions();
  const canRunIntel = can("intelligence:run");
  const qc = useQueryClient();

  const assetRecs = useQuery({
    queryKey: ["asset-recommendations", assetId],
    queryFn: () => fetchAssetRecommendations(assetId),
  });

  const rootCause = useQuery({
    queryKey: ["root-cause", assetId],
    queryFn: () => fetchAssetRootCause(assetId, false),
    enabled: !canRunIntel,
  });

  const assessment = useMutation({
    mutationFn: async () => {
      const prediction = await predictAssetHealth(assetId, true);
      const root = await fetchAssetRootCause(assetId, false);
      return { prediction, root };
    },
    onSuccess: () => {
      toast("Assessment complete");
      void qc.invalidateQueries({ queryKey: ["asset-health-history", assetId] });
    },
    onError: (e) => toast((e as Error).message, "error"),
  });

  const prediction = assessment.data?.prediction;
  const root = assessment.data?.root ?? (canRunIntel ? undefined : rootCause.data);
  const loading = assessment.isPending || (!canRunIntel && rootCause.isLoading);

  return (
    <div className="space-y-4">
      <Card>
        <div className="flex flex-col sm:flex-row items-center gap-6 pb-4 mb-4 border-b border-border">
          <AssetTypeVisual typeName={assetTypeName} assetName={assetName} size="md" />
          <div className="text-center sm:text-left">
            <h3 className="font-semibold">{assetName ?? "Asset"}</h3>
            <p className="text-sm text-muted-foreground mt-1">360° asset preview · intelligence view</p>
          </div>
        </div>
        <div className="flex items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="size-4 text-[oklch(0.78_0.16_285)]" />
            <h3 className="font-semibold">AI health analysis</h3>
          </div>
          {canRunIntel && (
            <Button
              size="sm"
              variant="outline"
              disabled={assessment.isPending}
              onClick={() => assessment.mutate()}
            >
              {assessment.isPending ? "Running assessment…" : "Run assessment"}
            </Button>
          )}
        </div>

        {loading ? (
          <Skeleton className="h-32" />
        ) : !prediction && !root ? (
          <EmptyState
            title={canRunIntel ? "No assessment yet" : "No analysis available"}
            hint={canRunIntel ? "Run assessment to generate AI health analysis for this asset." : "Analysis will appear when available from the fleet pipeline."}
          />
        ) : (
          <div className="space-y-6 text-sm">
            {prediction && <PredictionSection data={prediction} />}
            {root && <RootCauseSection data={root} />}
            {prediction?.explanation?.enterprise_brief && (
              <EnterpriseBriefSection brief={prediction.explanation.enterprise_brief} />
            )}
            {!prediction?.explanation?.enterprise_brief && root?.enterprise_brief && (
              <EnterpriseBriefSection brief={root.enterprise_brief} />
            )}
          </div>
        )}
      </Card>

      {(prediction || assessment.isSuccess) && (
        <Card>
          <h3 className="font-semibold mb-3">Health trajectory</h3>
          <AssetHealthTrendChart
            assetId={assetId}
            latestScore={prediction?.health_score ?? null}
          />
          {prediction?.explanation?.health_delta != null && (
            <p className="text-xs text-muted-foreground mt-3">
              Change from previous assessment:{" "}
              {prediction.explanation.health_delta >= 0 ? "+" : ""}
              {(prediction.explanation.health_delta * 100).toFixed(1)} pts
            </p>
          )}
        </Card>
      )}

      <Card>
        <h3 className="font-semibold mb-3">Maintenance recommendations</h3>
        {assetRecs.isLoading ? (
          <Skeleton className="h-16" />
        ) : (assetRecs.data ?? []).length === 0 ? (
          <EmptyState title="No recommendations for this asset" />
        ) : (
          <div className="space-y-2">
            {(assetRecs.data ?? []).map((r) => (
              <div key={r.id} className="rounded-lg border border-border p-3 text-sm">
                <div className="flex justify-between gap-2">
                  <span className="font-medium">{r.title}</span>
                  <Pill tone={priorityTone[r.priority]}>{r.priority}</Pill>
                </div>
                {r.description && <p className="text-muted-foreground text-xs mt-1">{r.description}</p>}
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

function PredictionSection({ data }: { data: HealthPredictionResponse }) {
  const priority = riskPriority(data.risk_level);
  return (
    <section className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <div>
          <div className="text-xs text-muted-foreground uppercase">Health score</div>
          <div className="text-2xl font-semibold tabular-nums">{pct(data.health_score)}</div>
        </div>
        <div>
          <div className="text-xs text-muted-foreground uppercase">Risk</div>
          <Pill tone={priorityTone[priority]} className="mt-1">{data.risk_level}</Pill>
        </div>
        <div>
          <div className="text-xs text-muted-foreground uppercase">Confidence</div>
          <div className="text-lg font-medium tabular-nums mt-0.5">{pct(data.confidence)}</div>
        </div>
      </div>

      {data.explanation?.summary && (
        <div>
          <div className="font-medium mb-1">Summary</div>
          <p className="text-muted-foreground leading-relaxed">{data.explanation.summary}</p>
        </div>
      )}

      {data.explanation?.enterprise_brief?.why_predicted && (
        <div>
          <div className="font-medium mb-1">Why this prediction</div>
          <p className="text-muted-foreground leading-relaxed">
            {data.explanation.enterprise_brief.why_predicted}
          </p>
        </div>
      )}

      {(data.explanation?.factors ?? []).length > 0 && (
        <FactorsList title="Contributing factors" factors={data.explanation!.factors} />
      )}
    </section>
  );
}

function RootCauseSection({ data }: { data: RootCauseResponse }) {
  return (
    <section className="space-y-3 border-t border-border pt-4">
      <div className="font-medium">Root cause analysis</div>
      <p className="text-muted-foreground leading-relaxed">{data.root_cause_summary}</p>
      {data.factors.length > 0 && <FactorsList title="Root cause factors" factors={data.factors} />}
    </section>
  );
}

function EnterpriseBriefSection({ brief }: { brief: EnterpriseHealthBrief }) {
  const rows: { label: string; value: string }[] = [
    { label: "What happened", value: brief.what_happened },
    { label: "Why predicted", value: brief.why_predicted },
    { label: "Business impact", value: brief.business_impact },
    { label: "Recommended action", value: brief.recommended_action },
    { label: "Priority", value: brief.priority },
    { label: "Estimated downtime", value: brief.estimated_downtime },
    { label: "Estimated effort", value: brief.estimated_effort },
  ];
  if (brief.estimated_cost) rows.push({ label: "Estimated cost", value: brief.estimated_cost });
  if (brief.remaining_useful_life) rows.push({ label: "Remaining useful life", value: brief.remaining_useful_life });

  return (
    <section className="space-y-3 border-t border-border pt-4">
      <div className="font-medium">Enterprise health brief</div>
      <div className="grid gap-3 sm:grid-cols-2">
        {rows.map((row) => (
          <div key={row.label} className="rounded-lg border border-border p-3 bg-background/30">
            <div className="text-[11px] uppercase tracking-wider text-muted-foreground">{row.label}</div>
            <p className="mt-1 text-foreground/90 leading-relaxed">{row.value}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function FactorsList({ title, factors }: { title: string; factors: ExplanationFactor[] }) {
  return (
    <div>
      <div className="font-medium mb-2">{title}</div>
      <ul className="space-y-2">
        {factors.map((f, i) => (
          <li key={i} className="rounded-lg border border-border px-3 py-2">
            <div className="flex items-center justify-between gap-2">
              <span className="font-medium text-xs">{f.factor}</span>
              <Pill tone={priorityTone[riskPriority(f.severity)]}>{f.severity}</Pill>
            </div>
            <p className="text-muted-foreground text-xs mt-1">{f.message}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
