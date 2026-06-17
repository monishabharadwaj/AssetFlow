import { Link, useLocation, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "../../shared/api/query-keys";
import { fetchAsset } from "../../features/assets/api/assets-api";

const labelMap: Record<string, string> = {
  dashboard: "Dashboard",
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
    return <p className="text-sm text-muted-foreground">Home</p>;
  }

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm">
      <Link to="/dashboard" className="text-muted-foreground hover:text-foreground">
        Home
      </Link>
      {segments.map((segment, index) => {
        const path = `/${segments.slice(0, index + 1).join("/")}`;
        const isAssetId = segments[index - 1] === "assets" && segment === assetId;
        const label = isAssetId && asset ? asset.asset_tag : labelMap[segment] ?? segment;
        const isLast = index === segments.length - 1;

        return (
          <span key={path} className="flex items-center gap-2">
            <span className="text-muted-foreground">/</span>
            {isLast ? (
              <span className="font-medium text-foreground">{label}</span>
            ) : (
              <Link to={path} className="text-muted-foreground hover:text-foreground">
                {label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
