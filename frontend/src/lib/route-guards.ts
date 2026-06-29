import { redirect } from "@tanstack/react-router";

import { fetchCurrentUser } from "@/features/auth/api";
import { canAccessPath } from "@/features/auth/permissions";
import { getToken } from "@/lib/api";
import type { UserRole } from "@/lib/types/backend";

export function requireAuth() {
  if (!getToken()) {
    throw redirect({ to: "/login" });
  }
}

export function requirePermission(path: string, role: UserRole | undefined) {
  if (!canAccessPath(role, path)) {
    throw redirect({ to: "/dashboard" });
  }
}

export async function guardRoute(path: string) {
  requireAuth();
  const me = await fetchCurrentUser();
  requirePermission(path, me.role);
  return me;
}
