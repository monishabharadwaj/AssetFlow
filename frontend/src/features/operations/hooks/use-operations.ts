import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchCostOptimization,
  fetchDriftStatus,
  fetchMaintenanceSchedule,
  fetchNotifications,
  fetchPipelineStatus,
  fetchReplacementPlan,
  fetchReportsAnalytics,
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
      void queryClient.invalidateQueries({ queryKey: ["dashboard", "my-workspace"] });
    },
  });
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["operations", "notifications"] });
      void queryClient.invalidateQueries({ queryKey: ["dashboard", "my-workspace"] });
    },
  });
}

export function useReportsAnalytics(useAi = false, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ["operations", "reports-analytics", useAi],
    queryFn: () => fetchReportsAnalytics(useAi),
    staleTime: 2 * 60_000,
    enabled: options?.enabled ?? true,
    retry: false,
  });
}

export function useWeeklyReport(useLlm = false) {
  return useQuery({
    queryKey: ["operations", "weekly-report", useLlm],
    queryFn: () => fetchWeeklyReport(useLlm),
    staleTime: 5 * 60_000,
  });
}

export function useDriftReport() {
  return useQuery({
    queryKey: ["operations", "drift"],
    queryFn: fetchDriftStatus,
    staleTime: 5 * 60_000,
  });
}

export function useReplacementPlan(limit = 10) {
  return useQuery({
    queryKey: ["operations", "replacement-plan", limit],
    queryFn: () => fetchReplacementPlan(limit),
    staleTime: 5 * 60_000,
  });
}

export function useCostOptimizationReport(limit = 10) {
  return useQuery({
    queryKey: ["operations", "cost-optimization", limit],
    queryFn: () => fetchCostOptimization(limit),
    staleTime: 5 * 60_000,
  });
}

export function useMaintenanceScheduleReport(limit = 10) {
  return useQuery({
    queryKey: ["operations", "maintenance-schedule", limit],
    queryFn: () => fetchMaintenanceSchedule(limit),
    staleTime: 5 * 60_000,
  });
}
