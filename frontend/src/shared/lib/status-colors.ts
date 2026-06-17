export const STATUS_CHART_COLORS: Record<string, string> = {
  AVAILABLE: "#10b981",
  ASSIGNED: "#3b82f6",
  IN_MAINTENANCE: "#f59e0b",
  RETIRED: "#71717a",
  DISPOSED: "#f43f5e",
};

export const STATUS_BADGE_CLASSES: Record<string, string> = {
  AVAILABLE: "bg-emerald-100 text-emerald-800 border-emerald-200",
  ASSIGNED: "bg-blue-100 text-blue-800 border-blue-200",
  IN_MAINTENANCE: "bg-amber-100 text-amber-800 border-amber-200",
  RETIRED: "bg-zinc-100 text-zinc-700 border-zinc-200",
  DISPOSED: "bg-rose-100 text-rose-800 border-rose-200",
};

export function getStatusChartColor(status: string): string {
  return STATUS_CHART_COLORS[status] ?? "#94a3b8";
}

export function formatStatusLabel(status: string): string {
  return status
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
