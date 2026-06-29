import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchReportsDocument,
  fetchPipelineStatus,
  markAllNotificationsRead,
  markNotificationRead,
  runPipeline,
} from "./api";

export function useReportsAnalytics(useAi: boolean, enabled = true) {
  return useQuery({
    queryKey: ["operations-report", useAi],
    queryFn: () => fetchReportsDocument(useAi),
    enabled,
  });
}

export function useRunPipeline() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => runPipeline(true),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["dashboard-summary"] });
      void qc.invalidateQueries({ queryKey: ["recommendations"] });
      void qc.invalidateQueries({ queryKey: ["operations-report"] });
    },
  });
}

export function useMarkNotificationRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => markNotificationRead(id),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["notifications"] }),
  });
}

export function useMarkAllNotificationsRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => markAllNotificationsRead(),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["notifications"] }),
  });
}

export function usePipelineStatus(enabled = true) {
  return useQuery({
    queryKey: ["pipeline-status"],
    queryFn: fetchPipelineStatus,
    enabled,
    refetchInterval: 60_000,
  });
}
