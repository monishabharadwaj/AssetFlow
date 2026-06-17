import { apiGet } from "../../../shared/api/client";
import type { DashboardSummary } from "../../../shared/api/types";

export function fetchDashboardSummary(): Promise<DashboardSummary> {
  return apiGet<DashboardSummary>("/dashboard/summary");
}
