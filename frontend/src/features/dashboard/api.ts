import { apiGet } from "@/lib/api";
import { mapDashboardSummary } from "@/lib/adapters/dashboard";
import type { DashboardSummaryResponse, MyWorkspaceResponse } from "@/lib/types/backend";
import type { DashboardSummary } from "@/lib/types/ui";

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const data = await apiGet<DashboardSummaryResponse>("/dashboard/summary");
  return mapDashboardSummary(data);
}

export function fetchMyWorkspace() {
  return apiGet<MyWorkspaceResponse>("/dashboard/my-workspace");
}