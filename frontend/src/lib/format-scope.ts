import type { User } from "@/lib/types/ui";

const UUID_PREFIX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i;

/** Human-readable scope for reports and assistant (frontend-only; no backend change). */
export function formatScopeLabel(scope: string | undefined, user: User | null | undefined): string {
  if (user?.role === "ADMIN") return "Organization-wide";
  if (user?.department_name) return `${user.department_name} department`;
  if (scope && !UUID_PREFIX.test(scope.trim())) return scope;
  return "Your department";
}

export function assistantScopeBadge(user: User | null | undefined): string {
  return formatScopeLabel(undefined, user);
}
