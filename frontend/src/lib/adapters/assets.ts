import type { Asset, AssetSearchParams } from "@/lib/types/backend";
import type { AssetListItem } from "@/lib/types/ui";

export function mapAssetForList(
  asset: Asset,
  departmentNames?: Map<string, string>,
): AssetListItem {
  return {
    id: asset.id,
    asset_tag: asset.asset_tag,
    name: asset.name,
    status: asset.current_status,
    department_id: asset.current_department_id,
    department_name: departmentNames?.get(asset.current_department_id) ?? null,
    location: asset.current_location,
    serial_number: asset.serial_number,
  };
}

export function buildAssetSearchParams(opts: {
  q?: string;
  status?: string;
  page?: number;
  page_size?: number;
}): AssetSearchParams {
  const params: AssetSearchParams = {
    page: opts.page ?? 1,
    page_size: opts.page_size ?? 20,
  };
  // Backend /assets/search ANDs name + asset_tag filters, so a single query
  // term must target one column. A tag-like token (no spaces, has a digit or
  // hyphen) is matched against asset_tag; otherwise we match the name.
  if (opts.q) {
    const q = opts.q.trim();
    const looksLikeTag = /^[^\s]+$/.test(q) && /[\d-]/.test(q);
    if (looksLikeTag) params.asset_tag = q;
    else params.name = q;
  }
  if (opts.status && opts.status !== "ALL") {
    params.current_status = opts.status as AssetSearchParams["current_status"];
  }
  return params;
}
