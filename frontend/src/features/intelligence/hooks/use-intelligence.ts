import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "../../../shared/api/query-keys";
import {
  fetchAssetRecommendations,
  fetchAssetRootCause,
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
    mutationFn: (persist?: boolean) => scoreBatch(persist ?? true),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary });
      void queryClient.invalidateQueries({ queryKey: ["intelligence"] });
      void queryClient.invalidateQueries({ queryKey: ["operations"] });
    },
  });
}

export function useRunPrediction(assetId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => predictAssetHealth(assetId, true),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["intelligence", "prediction", assetId] });
      void queryClient.invalidateQueries({ queryKey: ["intelligence", "root-cause", assetId] });
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary });
    },
  });
}

export function useAssetRootCause(assetId: string, useLlm = true, enabled = true) {
  return useQuery({
    queryKey: ["intelligence", "root-cause", assetId, useLlm],
    queryFn: () => fetchAssetRootCause(assetId, useLlm),
    enabled: Boolean(assetId) && enabled,
    retry: false,
  });
}

