import type { ReactNode } from "react";

import { AssetTypeIcon } from "../../../shared/components/data-display/asset-type-icon";
import { HealthRing } from "../../../shared/components/data-display/health-ring";
import { LifecycleProgressStrip } from "../../../shared/components/data-display/lifecycle-progress-strip";
import { StatusBadge } from "../../../shared/components/data-display/status-badge";
import { Badge } from "../../../shared/components/ui/badge";
import { Card, CardContent } from "../../../shared/components/ui/card";
import type { Asset, AssetStatus } from "../../../shared/api/types";
import { cn } from "../../../shared/lib/utils";

type AssetShowcaseCardProps = {
  asset: Pick<
    Asset,
    "name" | "asset_tag" | "current_status" | "current_location"
  >;
  typeName?: string | null;
  departmentName?: string | null;
  assigneeName?: string | null;
  healthScore?: number | null;
  predictedHealthScore?: number | null;
  riskLevel?: "LOW" | "MEDIUM" | "HIGH" | null;
  actions?: ReactNode;
  compact?: boolean;
  className?: string;
};

export function AssetShowcaseCard({
  asset,
  typeName,
  departmentName,
  assigneeName,
  healthScore,
  predictedHealthScore,
  riskLevel,
  actions,
  compact = false,
  className,
}: AssetShowcaseCardProps) {
  const displayScore = predictedHealthScore ?? healthScore;

  return (
    <Card
      className={cn(
        "overflow-hidden rounded-3xl border border-slate-700 bg-[#111827] shadow-[0_0_25px_rgba(59,130,246,0.12)]",
        className,
      )}
    >
      <CardContent className={cn("p-6", compact ? "sm:p-4" : "sm:p-8")}>
        <div
          className={cn(
            "flex gap-4",
            compact ? "text-lg" : "text-3xl text-white",
          )}
        >
          <AssetTypeIcon
            typeName={typeName}
            className={compact ? "h-12 w-12" : undefined}
            iconClassName={compact ? "h-6 w-6" : undefined}
          />
          <div className="min-w-0 flex-1 space-y-3">
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h2
                    className={cn(
                      "font-semibold tracking-tight",
                      compact ? "text-lg" : "text-2xl",
                    )}
                  >
                    {asset.name}
                  </h2>
                  <StatusBadge status={asset.current_status as AssetStatus} />
                  {riskLevel ? (
                    <Badge
                      variant={riskLevel === "HIGH" ? "outline" : "secondary"}
                      className={
                        riskLevel === "HIGH"
                          ? "border-rose-300 text-rose-700"
                          : ""
                      }
                    >
                      AI {riskLevel} risk
                    </Badge>
                  ) : null}
                </div>
                <p className="mt-0.5 text-sm text-slate-400">
                  {asset.asset_tag}
                </p>
              </div>
              {!compact ? <HealthRing score={displayScore} size={90} /> : null}
            </div>

            <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
              {departmentName ? (
                <span className="rounded-xl border border-slate-700 bg-slate-800/70 px-3 py-1 text-slate-300">
                  {departmentName}
                </span>
              ) : null}
              <span className="rounded-md border border-slate-700 bg-slate-800/70 px-2 py-1 text-slate-300">
                {asset.current_location}
              </span>
              {assigneeName ? (
                <span className="rounded-xl border border-slate-700 bg-slate-800/70 px-3 py-1 text-slate-300">
                  {assigneeName}
                </span>
              ) : null}
            </div>

            <LifecycleProgressStrip
              status={asset.current_status}
              compact={compact}
            />

            {actions ? (
              <div className="flex flex-wrap gap-3 pt-3">{actions}</div>
            ) : null}
          </div>
          {compact ? (
            <HealthRing score={displayScore} size={56} strokeWidth={5} />
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
