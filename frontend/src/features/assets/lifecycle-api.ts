import { apiGet, apiPatch, apiPost, buildQueryString } from "@/lib/api";
import type {
  Allocation,
  HealthHistory,
  HealthHistoryCreate,
  Maintenance,
  MaintenanceCreate,
  MaintenanceUpdate,
  PaginatedResponse,
  TimelineEvent,
  Transfer,
  TransferCreate,
} from "@/lib/types/backend";

export function fetchAssetTimeline(assetId: string, page = 1, pageSize = 20) {
  return apiGet<PaginatedResponse<TimelineEvent> & { asset_id: string }>(
    `/assets/${assetId}/timeline${buildQueryString({ page, page_size: pageSize })}`,
  );
}

export function fetchAssetAllocations(assetId: string, page = 1, pageSize = 20) {
  return apiGet<PaginatedResponse<Allocation>>(
    `/assets/${assetId}/allocations${buildQueryString({ page, page_size: pageSize })}`,
  );
}

export function fetchAssetTransfers(assetId: string, page = 1, pageSize = 20) {
  return apiGet<PaginatedResponse<Transfer>>(
    `/assets/${assetId}/transfers${buildQueryString({ page, page_size: pageSize })}`,
  );
}

export function fetchAssetMaintenance(assetId: string, page = 1, pageSize = 20) {
  return apiGet<PaginatedResponse<Maintenance>>(
    `/assets/${assetId}/maintenance${buildQueryString({ page, page_size: pageSize })}`,
  );
}

export function fetchAssetHealthHistory(assetId: string, page = 1, pageSize = 20) {
  return apiGet<PaginatedResponse<HealthHistory>>(
    `/assets/${assetId}/health-history${buildQueryString({ page, page_size: pageSize })}`,
  );
}

export function assignAsset(assetId: string, data: { employee_id: string; allocated_at: string; notes?: string | null }) {
  return apiPost(`/assets/${assetId}/allocations/assign`, data);
}

export function returnAsset(assetId: string, data: { returned_at: string; notes?: string | null }) {
  return apiPost(`/assets/${assetId}/allocations/return`, data);
}

export function reassignAsset(assetId: string, data: { employee_id: string; allocated_at: string; notes?: string | null }) {
  return apiPost(`/assets/${assetId}/allocations/reassign`, data);
}

export function transferAsset(assetId: string, data: TransferCreate) {
  return apiPost<Transfer>(`/assets/${assetId}/transfers`, data);
}

export function createMaintenance(assetId: string, data: MaintenanceCreate) {
  return apiPost<Maintenance>(`/assets/${assetId}/maintenance`, data);
}

export function updateMaintenanceRecord(recordId: string, data: MaintenanceUpdate) {
  return apiPatch<Maintenance>(`/maintenance/${recordId}`, data);
}

export function createHealthSnapshot(assetId: string, data: HealthHistoryCreate) {
  return apiPost<HealthHistory>(`/assets/${assetId}/health-history`, data);
}

export function fetchMaintenanceWorkQueue(page = 1, pageSize = 30) {
  return apiGet<PaginatedResponse<import("@/lib/types/backend").MaintenanceWorkQueueItem>>(
    `/maintenance${buildQueryString({ page, page_size: pageSize })}`,
  );
}
