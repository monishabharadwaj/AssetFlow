import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "../../../shared/api/query-keys";
import type {
  AllocationAssignRequest,
  AllocationReassignRequest,
  AllocationReturnRequest,
  HealthHistoryCreate,
  MaintenanceCreate,
  MaintenanceUpdate,
  TransferCreate,
} from "../../../shared/api/types";
import {
  assignAsset,
  createHealthSnapshot,
  createMaintenance,
  fetchAssetAllocations,
  fetchAssetHealthHistory,
  fetchAssetMaintenance,
  fetchAssetTimeline,
  fetchAssetTransfers,
  fetchMaintenanceRecord,
  reassignAsset,
  returnAsset,
  transferAsset,
  updateMaintenanceRecord,
} from "../api/lifecycle-api";

function useInvalidateAsset(assetId: string) {
  const queryClient = useQueryClient();
  return () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.assets.detail(assetId) });
    queryClient.invalidateQueries({ queryKey: ["assets", "timeline", assetId] });
    queryClient.invalidateQueries({ queryKey: ["assets", "allocations", assetId] });
    queryClient.invalidateQueries({ queryKey: ["assets", "transfers", assetId] });
    queryClient.invalidateQueries({ queryKey: ["assets", "maintenance", assetId] });
    queryClient.invalidateQueries({ queryKey: ["assets", "health", assetId] });
    queryClient.invalidateQueries({ queryKey: ["assets"] });
    queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary });
  };
}

export function useAssetTimeline(assetId: string, page: number, pageSize: number) {
  return useQuery({
    queryKey: queryKeys.assets.timeline(assetId, page, pageSize),
    queryFn: () => fetchAssetTimeline(assetId, page, pageSize),
    enabled: Boolean(assetId),
  });
}

export function useAssetAllocations(assetId: string, page: number, pageSize: number) {
  return useQuery({
    queryKey: queryKeys.assets.allocations(assetId, page, pageSize),
    queryFn: () => fetchAssetAllocations(assetId, page, pageSize),
    enabled: Boolean(assetId),
  });
}

export function useAssetTransfers(assetId: string, page: number, pageSize: number) {
  return useQuery({
    queryKey: queryKeys.assets.transfers(assetId, page, pageSize),
    queryFn: () => fetchAssetTransfers(assetId, page, pageSize),
    enabled: Boolean(assetId),
  });
}

export function useAssetMaintenanceList(assetId: string, page: number, pageSize: number) {
  return useQuery({
    queryKey: queryKeys.assets.maintenance(assetId, page, pageSize),
    queryFn: () => fetchAssetMaintenance(assetId, page, pageSize),
    enabled: Boolean(assetId),
  });
}

export function useAssetHealthHistory(assetId: string, page: number, pageSize: number) {
  return useQuery({
    queryKey: queryKeys.assets.health(assetId, page, pageSize),
    queryFn: () => fetchAssetHealthHistory(assetId, page, pageSize),
    enabled: Boolean(assetId),
  });
}

export function useMaintenanceRecord(recordId: string) {
  return useQuery({
    queryKey: queryKeys.maintenance.detail(recordId),
    queryFn: () => fetchMaintenanceRecord(recordId),
    enabled: Boolean(recordId),
  });
}

export function useLifecycleMutations(assetId: string) {
  const invalidate = useInvalidateAsset(assetId);

  return {
    assign: useMutation({
      mutationFn: (data: AllocationAssignRequest) => assignAsset(assetId, data),
      onSuccess: invalidate,
    }),
    return: useMutation({
      mutationFn: (data: AllocationReturnRequest) => returnAsset(assetId, data),
      onSuccess: invalidate,
    }),
    reassign: useMutation({
      mutationFn: (data: AllocationReassignRequest) => reassignAsset(assetId, data),
      onSuccess: invalidate,
    }),
    transfer: useMutation({
      mutationFn: (data: TransferCreate) => transferAsset(assetId, data),
      onSuccess: invalidate,
    }),
    createMaintenance: useMutation({
      mutationFn: (data: MaintenanceCreate) => createMaintenance(assetId, data),
      onSuccess: invalidate,
    }),
    updateMaintenance: useMutation({
      mutationFn: ({ id, data }: { id: string; data: MaintenanceUpdate }) =>
        updateMaintenanceRecord(id, data),
      onSuccess: invalidate,
    }),
    createHealth: useMutation({
      mutationFn: (data: HealthHistoryCreate) => createHealthSnapshot(assetId, data),
      onSuccess: invalidate,
    }),
  };
}
