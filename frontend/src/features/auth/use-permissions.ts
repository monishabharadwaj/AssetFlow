import { useMemo } from "react";

import { useAuth } from "@/lib/auth-context";
import { canAccessPath, hasPermission, type Permission } from "./permissions";

export function usePermissions() {
  const { user } = useAuth();

  return useMemo(
    () => ({
      role: user?.role,
      can: (permission: Permission) => hasPermission(user?.role, permission),
      canAccessPath: (pathname: string) => canAccessPath(user?.role, pathname),
    }),
    [user?.role],
  );
}
