import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "../../../shared/api/query-keys";
import type { AssetCreate, AssetListParams, AssetSearchParams, AssetUpdate } from "../../../shared/api/types";
import {
  createAsset,
  deactivateAsset,
  fetchAsset,
  fetchAssetCategories,
  fetchAssets,
  fetchAssetTypes,
  searchAssets,
  updateAsset,
} from "../api/assets-api";

export function useAssetsList(params: AssetListParams, enabled = true) {
  return useQuery({
    queryKey: queryKeys.assets.list(params),
    queryFn: () => fetchAssets(params),
    enabled,
  });
}

export function useAssetsSearch(params: AssetSearchParams, enabled = true) {
  return useQuery({
    queryKey: queryKeys.assets.search(params),
    queryFn: () => searchAssets(params),
    enabled,
  });
}

export function useAsset(assetId: string) {
  return useQuery({
    queryKey: queryKeys.assets.detail(assetId),
    queryFn: () => fetchAsset(assetId),
    enabled: Boolean(assetId),
  });
}

export function useLookups() {
  const categories = useQuery({
    queryKey: queryKeys.lookups.categories,
    queryFn: fetchAssetCategories,
  });
  const types = useQuery({
    queryKey: queryKeys.lookups.types,
    queryFn: fetchAssetTypes,
  });
  return { categories, types };
}

export function useAssetMutations() {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["assets"] });
    queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary });
  };

  const create = useMutation({
    mutationFn: (data: AssetCreate) => createAsset(data),
    onSuccess: invalidate,
  });

  const update = useMutation({
    mutationFn: ({ id, data }: { id: string; data: AssetUpdate }) => updateAsset(id, data),
    onSuccess: invalidate,
  });

  const deactivate = useMutation({
    mutationFn: (id: string) => deactivateAsset(id),
    onSuccess: invalidate,
  });

  return { create, update, deactivate };
}
