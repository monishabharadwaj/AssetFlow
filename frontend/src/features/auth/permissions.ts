import { BarChart3, Building2, ClipboardList, LayoutGrid, Users } from "lucide-react";

import type { UserRole } from "./types";

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
  | "notifications:write";

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
  ]),
  VIEWER: new Set([
    "assets:read",
    "maintenance:read",
    "reports:read",
    "dashboard:read",
    "assistant:use",
    "notifications:write",
  ]),
};

export const NAV_ITEMS = [
  { label: "Operations", to: "/dashboard", permission: "dashboard:read" as Permission, icon: LayoutGrid },
  { label: "Assets", to: "/assets", permission: "assets:read" as Permission, icon: BarChart3 },
  { label: "Maintenance", to: "/maintenance", permission: "maintenance:read" as Permission, icon: ClipboardList },
  { label: "Departments", to: "/departments", permission: "departments:read" as Permission, icon: Building2 },
  { label: "Employees", to: "/employees", permission: "employees:read" as Permission, icon: Users },
  { label: "Reports", to: "/reports", permission: "reports:read" as Permission, icon: BarChart3 },
] as const;

const ROUTE_PERMISSIONS: Record<string, Permission> = {
  "/dashboard": "dashboard:read",
  "/assets": "assets:read",
  "/maintenance": "maintenance:read",
  "/departments": "departments:read",
  "/employees": "employees:read",
  "/reports": "reports:read",
};

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

export function visibleNavItems(role: UserRole | undefined) {
  return NAV_ITEMS.filter((item) => hasPermission(role, item.permission));
}
