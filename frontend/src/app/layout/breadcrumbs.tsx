import { Link, useLocation, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "../../shared/api/query-keys";
import { fetchAsset } from "../../features/assets/api/assets-api";

const labelMap: Record<string, string> = {
  dashboard: "Operations",
  assets: "Assets",
  maintenance: "Maintenance",
  departments: "Departments",
  employees: "Employees",
  reports: "Reports",
};

export function Breadcrumbs() {
  const location = useLocation();
  const { assetId } = useParams<{ assetId: string }>();
  const segments = location.pathname.split("/").filter(Boolean);

  const { data: asset } = useQuery({
    queryKey: queryKeys.assets.detail(assetId ?? ""),
    queryFn: () => fetchAsset(assetId!),
    enabled: Boolean(assetId),
  });

  if (segments.length === 0) {
    return <p className="text-sm text-zinc-300">Home</p>;
  }

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm">
      <Link to="/dashboard" className="text-zinc-400 transition-colors hover:text-amber-200">
        Home
      </Link>
      {segments.map((segment, index) => {
        const path = `/${segments.slice(0, index + 1).join("/")}`;
        const isAssetId = segments[index - 1] === "assets" && segment === assetId;
        const label = isAssetId && asset ? asset.asset_tag : labelMap[segment] ?? segment;
        const isLast = index === segments.length - 1;

        return (
          <span key={path} className="flex items-center gap-2">
            <span className="text-zinc-500">/</span>
            {isLast ? (
              <span className="font-semibold text-white">{label}</span>
            ) : (
              <Link to={path} className="text-zinc-400 transition-colors hover:text-amber-200">
                {label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
