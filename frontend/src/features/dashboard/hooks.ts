import { useQuery } from "@tanstack/react-query";

import { fetchDashboardSummary, fetchMyWorkspace } from "./api";

export function useDashboardSummary() {
  return useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: fetchDashboardSummary,
  });
}

export function useMyWorkspace() {
  return useQuery({
    queryKey: ["my-workspace"],
    queryFn: fetchMyWorkspace,
  });
}

export { useFleetHealthStats } from "./hooks/use-fleet-health-stats";
export type { FleetBands, HighRiskItem } from "./hooks/use-fleet-health-stats";