import { apiDelete, apiGet, apiPatch, apiPost, buildQueryString } from "../../../shared/api/client";
import type {
  Asset,
  AssetCreate,
  AssetListParams,
  AssetSearchParams,
  AssetType,
  AssetUpdate,
  AssetCategory,
  PaginatedResponse,
} from "../../../shared/api/types";

export function fetchAssets(params: AssetListParams) {
  return apiGet<PaginatedResponse<Asset>>(`/assets${buildQueryString(params)}`);
}

export function searchAssets(params: AssetSearchParams) {
  return apiGet<PaginatedResponse<Asset>>(`/assets/search${buildQueryString(params)}`);
}

export function fetchAsset(assetId: string) {
  return apiGet<Asset>(`/assets/${assetId}`);
}

export function createAsset(data: AssetCreate) {
  return apiPost<Asset>("/assets", data);
}

export function updateAsset(assetId: string, data: AssetUpdate) {
  return apiPatch<Asset>(`/assets/${assetId}`, data);
}

export function deactivateAsset(assetId: string) {
  return apiDelete<Asset>(`/assets/${assetId}`);
}

export function fetchAssetCategories() {
  return apiGet<AssetCategory[]>("/asset-categories");
}

export function fetchAssetTypes() {
  return apiGet<AssetType[]>("/asset-types");
}
