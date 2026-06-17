import { apiGet, apiPatch, apiPost, buildQueryString } from "../../../shared/api/client";
import type {
  Allocation,
  AllocationAssignRequest,
  AllocationReassignRequest,
  AllocationReturnRequest,
  AssetTimelineResponse,
  HealthHistory,
  HealthHistoryCreate,
  Maintenance,
  MaintenanceCreate,
  MaintenanceUpdate,
  PaginatedResponse,
  Transfer,
  TransferCreate,
} from "../../../shared/api/types";

export function fetchAssetTimeline(assetId: string, page = 1, pageSize = 20) {
  return apiGet<AssetTimelineResponse>(
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

export function assignAsset(assetId: string, data: AllocationAssignRequest) {
  return apiPost(`/assets/${assetId}/allocations/assign`, data);
}

export function returnAsset(assetId: string, data: AllocationReturnRequest) {
  return apiPost(`/assets/${assetId}/allocations/return`, data);
}

export function reassignAsset(assetId: string, data: AllocationReassignRequest) {
  return apiPost(`/assets/${assetId}/allocations/reassign`, data);
}

export function transferAsset(assetId: string, data: TransferCreate) {
  return apiPost<Transfer>(`/assets/${assetId}/transfers`, data);
}

export function createMaintenance(assetId: string, data: MaintenanceCreate) {
  return apiPost<Maintenance>(`/assets/${assetId}/maintenance`, data);
}

export function fetchMaintenanceRecord(recordId: string) {
  return apiGet<Maintenance>(`/maintenance/${recordId}`);
}

export function updateMaintenanceRecord(recordId: string, data: MaintenanceUpdate) {
  return apiPatch<Maintenance>(`/maintenance/${recordId}`, data);
}

export function createHealthSnapshot(assetId: string, data: HealthHistoryCreate) {
  return apiPost<HealthHistory>(`/assets/${assetId}/health-history`, data);
}
