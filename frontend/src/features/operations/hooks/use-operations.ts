import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchNotifications,
  fetchPipelineStatus,
  fetchWeeklyReport,
  markAllNotificationsRead,
  markNotificationRead,
  runPipeline,
} from "../api/operations-api";

export function useNotifications(limit = 20) {
  return useQuery({
    queryKey: ["operations", "notifications", limit],
    queryFn: () => fetchNotifications(limit),
    refetchInterval: 30_000,
  });
}

export function usePipelineStatus() {
  return useQuery({
    queryKey: ["operations", "pipeline-status"],
    queryFn: fetchPipelineStatus,
    refetchInterval: 60_000,
  });
}

export function useRunPipeline() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (persist: boolean) => runPipeline(persist),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["operations"] });
      void queryClient.invalidateQueries({ queryKey: ["intelligence"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    },
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["operations", "notifications"] });
    },
  });
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["operations", "notifications"] });
    },
  });
}

export function useWeeklyReport(useLlm = false) {
  return useQuery({
    queryKey: ["operations", "weekly-report", useLlm],
    queryFn: () => fetchWeeklyReport(useLlm),
    staleTime: 5 * 60_000,
  });
}
