import type { AssetStatus, HealthBand, Priority, RiskLevel } from "./types";

export function pct(n: number | null | undefined, digits = 0): string {
  if (n === null || n === undefined || Number.isNaN(n)) return "—";
  const v = n <= 1 ? n * 100 : n;
  return `${v.toFixed(digits)}%`;
}

export function healthBand(score: number | null | undefined): HealthBand {
  if (score === null || score === undefined) return "Monitor";
  const v = score <= 1 ? score * 100 : score;
  if (v >= 80) return "Healthy";
  if (v >= 60) return "Monitor";
  if (v >= 40) return "Warning";
  return "Critical";
}

export const statusLabel: Record<AssetStatus, string> = {
  AVAILABLE: "Available",
  ASSIGNED: "Assigned",
  IN_MAINTENANCE: "In Maintenance",
  RETIRED: "Retired",
  DISPOSED: "Disposed",
};

export const statusTone: Record<AssetStatus, string> = {
  AVAILABLE: "bg-success/15 text-[oklch(0.82_0.17_155)] border-success/30",
  ASSIGNED: "bg-primary/15 text-[oklch(0.82_0.18_285)] border-primary/30",
  IN_MAINTENANCE: "bg-warning/15 text-[oklch(0.85_0.15_75)] border-warning/30",
  RETIRED: "bg-muted text-muted-foreground border-border",
  DISPOSED: "bg-muted text-muted-foreground border-border",
};

export const bandTone: Record<HealthBand, string> = {
  Healthy: "bg-success/15 text-[oklch(0.82_0.17_155)] border-success/30",
  Monitor: "bg-monitor/15 text-[oklch(0.82_0.16_240)] border-monitor/30",
  Warning: "bg-warning/15 text-[oklch(0.85_0.15_75)] border-warning/30",
  Critical: "bg-critical/15 text-[oklch(0.78_0.22_18)] border-critical/30",
};

export const priorityTone: Record<Priority, string> = {
  HIGH: "bg-critical/15 text-[oklch(0.78_0.22_18)] border-critical/30",
  MEDIUM: "bg-warning/15 text-[oklch(0.85_0.15_75)] border-warning/30",
  LOW: "bg-monitor/15 text-[oklch(0.82_0.16_240)] border-monitor/30",
};

export const riskTone: Record<RiskLevel, string> = {
  HIGH: "bg-critical/15 text-[oklch(0.78_0.22_18)] border-critical/30",
  MEDIUM: "bg-warning/15 text-[oklch(0.85_0.15_75)] border-warning/30",
  LOW: "bg-success/15 text-[oklch(0.82_0.17_155)] border-success/30",
};

export function fmtDate(s: string | null | undefined): string {
  if (!s) return "—";
  try { return new Date(s).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }); }
  catch { return s; }
}

export function fmtRelative(s: string | null | undefined): string {
  if (!s) return "—";
  const t = new Date(s).getTime();
  if (Number.isNaN(t)) return s;
  const diff = (Date.now() - t) / 1000;
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 86400 * 7) return `${Math.floor(diff / 86400)}d ago`;
  return fmtDate(s);
}

export function formatCurrency(value: string | number | null | undefined): string {
  if (value === null || value === undefined || value === "") return "—";
  const n = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(n)) return "—";
  return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(n);
}
