import { apiGet, apiPatch, apiPost, buildQueryString } from "@/lib/api";
import { mapReportsAnalytics } from "@/lib/adapters/reports";
import type { ReportsAnalytics } from "@/lib/types/backend";
import type { OperationsReport } from "@/lib/types/ui";

export async function fetchReportsDocument(useAi: boolean): Promise<OperationsReport> {
  const timeoutMs = useAi ? 120_000 : 45_000;
  const data = await apiGet<ReportsAnalytics>(
    `/operations/reports/analytics?use_ai=${useAi}`,
    timeoutMs,
  );
  return mapReportsAnalytics(data, useAi);
}

export function runPipeline(persist = true) {
  return apiPost(`/operations/pipeline/run?persist=${persist}`, {});
}

export function fetchNotifications(limit = 20) {
  return apiGet<{ items: import("@/lib/types/backend").NotificationItem[]; total: number; unread_count: number }>(
    `/operations/notifications${buildQueryString({ limit })}`,
  );
}

export function markNotificationRead(notificationId: string) {
  return apiPatch(`/operations/notifications/${notificationId}/read`, {});
}

export function markAllNotificationsRead() {
  return apiPost<{ marked_read: number }>("/operations/notifications/read-all", {});
}

export function fetchPipelineStatus() {
  return apiGet<import("@/lib/types/backend").PipelineStatus>("/operations/pipeline/status");
}
