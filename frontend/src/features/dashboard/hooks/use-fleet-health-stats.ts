import { useMemo } from "react";

import { useHighRiskAssets, useIntelligenceCache } from "@/features/intelligence/hooks";
import type { DashboardSummary } from "@/lib/types/ui";

import { useDashboardSummary } from "../hooks";

export type FleetBands = {
  healthy: number;
  monitor: number;
  warning: number;
  critical: number;
  unscored?: number;
};

export type HighRiskItem = {
  asset_id: string;
  asset_tag: string;
  asset_name: string;
  asset_type_name?: string | null;
  health_score: number;
  risk_level: string;
};

function bandsTotal(bands: FleetBands): number {
  return bands.healthy + bands.monitor + bands.warning + bands.critical + (bands.unscored ?? 0);
}

function fromSummaryBands(summary: DashboardSummary | undefined): FleetBands | null {
  if (!summary?.health_distribution) return null;
  const b = summary.health_distribution;
  const total = b.healthy + b.monitor + b.warning + b.critical;
  if (total === 0) return null;
  return { ...b };
}

function deriveBandsFromCache(
  scoredAssets: number,
  highRiskTotal: number,
  totalActive: number,
): FleetBands {
  const critical = highRiskTotal;
  const healthy = Math.max(0, scoredAssets - critical);
  const unscored = Math.max(0, totalActive - scoredAssets);
  return {
    healthy,
    monitor: 0,
    warning: 0,
    critical,
    ...(unscored > 0 ? { unscored } : {}),
  };
}

export function useFleetHealthStats(enabled = true) {
  const summary = useDashboardSummary();
  const cache = useIntelligenceCache();
  const cacheWarm = cache.data?.warm === true;
  const highRisk = useHighRiskAssets(enabled && cacheWarm, 100);

  const stats = useMemo(() => {
    const s = summary.data;
    const scoredAssets = cache.data?.scored_assets ?? 0;
    const highRiskCount = highRisk.data?.total ?? highRisk.data?.items?.length ?? 0;
    const highRiskItems: HighRiskItem[] = (highRisk.data?.items ?? []).map((i) => ({
      asset_id: i.asset_id,
      asset_tag: i.asset_tag,
      asset_name: i.asset_name,
      asset_type_name: i.asset_type_name,
      health_score: i.health_score,
      risk_level: i.risk_level,
    }));

    let bands = fromSummaryBands(s) ?? { healthy: 0, monitor: 0, warning: 0, critical: 0 };
    const summaryEmpty = bandsTotal(bands) === 0;

    if (summaryEmpty && cacheWarm && scoredAssets > 0) {
      bands = deriveBandsFromCache(
        scoredAssets,
        highRiskCount,
        s?.kpis.total_assets ?? scoredAssets,
      );
    }

    const totalAssets = s?.kpis.total_assets ?? 0;
    const healthyCount = bands.healthy + (bands.unscored ? 0 : 0);
    const attentionCount = s?.attention_items.length ?? 0;

    let avgHealthPct: number | null = null;
    if (highRiskItems.length > 0 && scoredAssets > 0) {
      const highAvg = highRiskItems.reduce((a, i) => {
        const sc = i.health_score <= 1 ? i.health_score * 100 : i.health_score;
        return a + sc;
      }, 0) / highRiskItems.length;
      avgHealthPct = Math.round(highAvg * 0.4 + 65 * 0.6);
    }

    return {
      bands,
      scoredAssets,
      highRiskCount,
      highRiskItems,
      totalAssets,
      healthyCount,
      attentionCount,
      maintenanceDue: s?.kpis.maintenance_due ?? 0,
      avgHealthPct,
      cacheWarm,
      statusDistribution: s?.status_distribution,
      departmentDistribution: s?.department_distribution ?? [],
      attentionItems: s?.attention_items ?? [],
      recentActivity: s?.recent_activity ?? [],
    };
  }, [summary.data, cache.data, highRisk.data, cacheWarm]);

  return {
    ...stats,
    isLoading: summary.isLoading || cache.isLoading,
    isScoring: false,
  };
}
