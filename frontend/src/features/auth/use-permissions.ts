import { useAuth } from "./auth-context";
import { canAccessPath, hasPermission, type Permission } from "./permissions";

export function usePermissions() {
  const { user } = useAuth();
  const role = user?.role;

  return {
    user,
    role,
    can: (permission: Permission) => hasPermission(role, permission),
    canAccessPath: (pathname: string) => canAccessPath(role, pathname),
  };
}
