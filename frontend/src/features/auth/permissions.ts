import type { UserRole } from "@/lib/types/backend";

export type Permission =
  | "departments:read"
  | "departments:write"
  | "employees:read"
  | "employees:write"
  | "users:manage"
  | "assets:read"
  | "assets:write"
  | "maintenance:read"
  | "maintenance:write"
  | "reports:read"
  | "dashboard:read"
  | "assistant:use"
  | "intelligence:run"
  | "notifications:write"
  | "settings:read";

const ROLE_PERMISSIONS: Record<UserRole, ReadonlySet<Permission>> = {
  ADMIN: new Set([
    "departments:read",
    "departments:write",
    "employees:read",
    "employees:write",
    "users:manage",
    "assets:read",
    "assets:write",
    "maintenance:read",
    "maintenance:write",
    "reports:read",
    "dashboard:read",
    "assistant:use",
    "intelligence:run",
    "notifications:write",
    "settings:read",
  ]),
  MANAGER: new Set([
    "departments:read",
    "employees:read",
    "assets:read",
    "assets:write",
    "maintenance:read",
    "maintenance:write",
    "reports:read",
    "dashboard:read",
    "assistant:use",
    "intelligence:run",
    "notifications:write",
    "settings:read",
  ]),
  VIEWER: new Set([
    "assets:read",
    "maintenance:read",
    "reports:read",
    "dashboard:read",
    "assistant:use",
    "notifications:write",
    "settings:read",
  ]),
};

export const NAV_PERMISSIONS: Record<string, Permission> = {
  "/dashboard": "dashboard:read",
  "/assets": "assets:read",
  "/maintenance": "maintenance:read",
  "/departments": "departments:read",
  "/employees": "employees:read",
  "/reports": "reports:read",
  "/settings": "settings:read",
};

const ROUTE_PERMISSIONS: Record<string, Permission> = NAV_PERMISSIONS;

export function hasPermission(role: UserRole | undefined, permission: Permission): boolean {
  if (!role) return false;
  return ROLE_PERMISSIONS[role].has(permission);
}

export function canAccessPath(role: UserRole | undefined, pathname: string): boolean {
  if (!role) return false;
  const basePath = pathname.split("?")[0] ?? pathname;
  if (basePath.startsWith("/assets/")) {
    return hasPermission(role, "assets:read");
  }
  const permission = ROUTE_PERMISSIONS[basePath];
  if (!permission) return true;
  return hasPermission(role, permission);
}

export function canAccessNav(role: UserRole | undefined, path: string): boolean {
  const permission = NAV_PERMISSIONS[path];
  if (!permission) return true;
  return hasPermission(role, permission);
}
