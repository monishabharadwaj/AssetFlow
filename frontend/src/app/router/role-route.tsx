import { Navigate, Outlet, useLocation } from "react-router-dom";

import { usePermissions } from "../../features/auth/use-permissions";

export function RoleRoute() {
  const { canAccessPath } = usePermissions();
  const location = useLocation();

  if (!canAccessPath(location.pathname)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
}
