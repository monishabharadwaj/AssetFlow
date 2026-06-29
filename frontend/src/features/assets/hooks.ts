import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { buildAssetSearchParams } from "@/lib/adapters/assets";
import type { AssetCreate, AssetUpdate } from "@/lib/types/backend";
import {
  createAsset,
  deactivateAsset,
  fetchAsset,
  fetchAssetCategories,
  fetchAssetTypes,
  searchAssets,
  updateAsset,
} from "./api";
import * as lifecycle from "./lifecycle-api";

export function useAssetsSearch(
  opts: { q?: string; status?: string; page?: number; page_size?: number },
  enabled = true,
) {
  const params = buildAssetSearchParams(opts);
  return useQuery({
    queryKey: ["assets", params],
    queryFn: () => searchAssets(params),
    enabled,
  });
}

export function useAsset(assetId: string) {
  return useQuery({
    queryKey: ["asset", assetId],
    queryFn: () => fetchAsset(assetId),
    enabled: Boolean(assetId),
  });
}

export function useAssetLookups() {
  const categories = useQuery({ queryKey: ["asset-categories"], queryFn: fetchAssetCategories });
  const types = useQuery({ queryKey: ["asset-types"], queryFn: fetchAssetTypes });
  return { categories, types };
}

export function useCreateAsset() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AssetCreate) => createAsset(data),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["assets"] }),
  });
}

export function useUpdateAsset(assetId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: AssetUpdate) => updateAsset(assetId, data),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["asset", assetId] });
      void qc.invalidateQueries({ queryKey: ["assets"] });
    },
  });
}

export function useDeactivateAsset() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (assetId: string) => deactivateAsset(assetId),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["assets"] }),
  });
}

export function useAssetTimeline(assetId: string) {
  return useQuery({
    queryKey: ["asset-timeline", assetId],
    queryFn: () => lifecycle.fetchAssetTimeline(assetId),
    enabled: Boolean(assetId),
  });
}

export function useAssetAllocations(assetId: string) {
  return useQuery({
    queryKey: ["asset-allocations", assetId],
    queryFn: () => lifecycle.fetchAssetAllocations(assetId),
    enabled: Boolean(assetId),
  });
}

export function useAssetTransfers(assetId: string) {
  return useQuery({
    queryKey: ["asset-transfers", assetId],
    queryFn: () => lifecycle.fetchAssetTransfers(assetId),
    enabled: Boolean(assetId),
  });
}

export function useAssetMaintenance(assetId: string) {
  return useQuery({
    queryKey: ["asset-maintenance", assetId],
    queryFn: () => lifecycle.fetchAssetMaintenance(assetId),
    enabled: Boolean(assetId),
  });
}

export function useAssetHealthHistory(assetId: string) {
  return useQuery({
    queryKey: ["asset-health-history", assetId],
    queryFn: () => lifecycle.fetchAssetHealthHistory(assetId),
    enabled: Boolean(assetId),
  });
}

export function useMaintenanceWorkQueue(status?: string) {
  return useQuery({
    queryKey: ["maintenance-queue", status],
    queryFn: async () => {
      const data = await lifecycle.fetchMaintenanceWorkQueue(1, 50);
      if (!status) return data;
      return {
        ...data,
        items: data.items.filter((i) => i.record.status === status),
      };
    },
  });
}

export function useAssignAsset(assetId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { employee_id: string; allocated_at: string; notes?: string | null }) =>
      lifecycle.assignAsset(assetId, data),
    onSuccess: () => invalidateAssetLifecycle(qc, assetId),
  });
}

export function useReturnAsset(assetId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { returned_at: string; notes?: string | null }) =>
      lifecycle.returnAsset(assetId, data),
    onSuccess: () => invalidateAssetLifecycle(qc, assetId),
  });
}

export function useTransferAsset(assetId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: lifecycle.transferAsset.bind(null, assetId),
    onSuccess: () => invalidateAssetLifecycle(qc, assetId),
  });
}

export function useCreateMaintenance(assetId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: lifecycle.createMaintenance.bind(null, assetId),
    onSuccess: () => invalidateAssetLifecycle(qc, assetId),
  });
}

export function useUpdateMaintenanceRecord(assetId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ recordId, data }: { recordId: string; data: Parameters<typeof lifecycle.updateMaintenanceRecord>[1] }) =>
      lifecycle.updateMaintenanceRecord(recordId, data),
    onSuccess: () => invalidateAssetLifecycle(qc, assetId),
  });
}

function invalidateAssetLifecycle(qc: ReturnType<typeof useQueryClient>, assetId: string) {
  void qc.invalidateQueries({ queryKey: ["asset", assetId] });
  void qc.invalidateQueries({ queryKey: ["asset-timeline", assetId] });
  void qc.invalidateQueries({ queryKey: ["asset-allocations", assetId] });
  void qc.invalidateQueries({ queryKey: ["asset-transfers", assetId] });
  void qc.invalidateQueries({ queryKey: ["asset-maintenance", assetId] });
  void qc.invalidateQueries({ queryKey: ["maintenance-queue"] });
  void qc.invalidateQueries({ queryKey: ["assets"] });
}
