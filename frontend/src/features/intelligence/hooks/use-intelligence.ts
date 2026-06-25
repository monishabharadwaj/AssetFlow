import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "../../../shared/api/query-keys";
import {
  fetchAssetRecommendations,
  fetchHighRiskAssets,
  fetchRecommendations,
  predictAssetHealth,
  scoreBatch,
} from "../api/intelligence-api";

export function usePredictHealth(assetId: string, enabled = true) {
  return useQuery({
    queryKey: ["intelligence", "prediction", assetId],
    queryFn: () => predictAssetHealth(assetId),
    enabled: Boolean(assetId) && enabled,
    retry: false,
  });
}

export function useHighRiskAssets() {
  return useQuery({
    queryKey: ["intelligence", "high-risk"],
    queryFn: () => fetchHighRiskAssets(),
  });
}

export function useRecommendations(limit = 10) {
  return useQuery({
    queryKey: ["intelligence", "recommendations", limit],
    queryFn: () => fetchRecommendations(limit),
  });
}

export function useAssetRecommendations(assetId: string) {
  return useQuery({
    queryKey: ["intelligence", "recommendations", assetId],
    queryFn: () => fetchAssetRecommendations(assetId),
    enabled: Boolean(assetId),
  });
}

export function useScoreBatch() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (persist?: boolean) => scoreBatch(persist),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary });
      void queryClient.invalidateQueries({ queryKey: ["intelligence"] });
    },
  });
}

export function useRunPrediction(assetId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => predictAssetHealth(assetId, false),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["intelligence", "prediction", assetId] });
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary });
    },
  });
}
