import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ApiError } from "@/lib/api";
import { toast } from "@/lib/toast";
import {
  fetchCacheStatus,
  fetchHighRiskAssets,
  fetchRecommendations,
  runScoreBatch,
} from "./api";

export function useRecommendations() {
  return useQuery({
    queryKey: ["recommendations"],
    queryFn: fetchRecommendations,
  });
}

export function useIntelligenceCache() {
  return useQuery({
    queryKey: ["intelligence-cache"],
    queryFn: fetchCacheStatus,
  });
}

export function useHighRiskAssets(enabled = true, limit = 20) {
  return useQuery({
    queryKey: ["high-risk-assets", limit],
    queryFn: () => fetchHighRiskAssets(limit),
    enabled,
  });
}

export function useRunScoreBatch() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => runScoreBatch(true),
    onSuccess: (data) => {
      const msg = data.failed > 0
        ? `Scored ${data.scored} assets (${data.failed} failed)`
        : `Scored ${data.scored} assets`;
      toast(msg);
      void qc.invalidateQueries({ queryKey: ["recommendations"] });
      void qc.invalidateQueries({ queryKey: ["dashboard-summary"] });
      void qc.invalidateQueries({ queryKey: ["intelligence-cache"] });
      void qc.invalidateQueries({ queryKey: ["high-risk-assets"] });
      void qc.invalidateQueries({ queryKey: ["operations-report"] });
    },
    onError: (e) => {
      const err = e as Error;
      if (e instanceof ApiError) {
        if (e.status === 403) toast("You don't have permission to run AI scoring", "error");
        else if (err.name === "AbortError" || err.message.includes("abort")) {
          toast("Scoring timed out — try again or run Refresh analysis first", "error");
        } else toast(err.message, "error");
      } else toast(err.message, "error");
    },
  });
}
