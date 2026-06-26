export type HealthBand =
  | "EXCELLENT"
  | "HEALTHY"
  | "MONITOR"
  | "WARNING"
  | "CRITICAL";

export type OpsSeverity = "CRITICAL" | "WARNING" | "MONITOR" | "INFO" | "SUCCESS";

export type ActivitySentiment = "positive" | "neutral" | "negative" | "info";

export const HEALTH_BAND_COLORS: Record<HealthBand, string> = {
  EXCELLENT: "bg-emerald-500",
  HEALTHY: "bg-green-500",
  MONITOR: "bg-amber-400",
  WARNING: "bg-orange-500",
  CRITICAL: "bg-red-500",
};

export const HEALTH_BAND_TEXT: Record<HealthBand, string> = {
  EXCELLENT: "text-emerald-700",
  HEALTHY: "text-green-700",
  MONITOR: "text-amber-700",
  WARNING: "text-orange-700",
  CRITICAL: "text-red-700",
};

export const SEVERITY_STYLES: Record<OpsSeverity, string> = {
  CRITICAL: "border-red-200 bg-red-50/80",
  WARNING: "border-orange-200 bg-orange-50/60",
  MONITOR: "border-amber-200 bg-amber-50/50",
  INFO: "border-sky-200 bg-sky-50/40",
  SUCCESS: "border-emerald-200 bg-emerald-50/60",
};

export const SEVERITY_BADGE: Record<OpsSeverity, string> = {
  CRITICAL: "bg-red-100 text-red-800",
  WARNING: "bg-orange-100 text-orange-800",
  MONITOR: "bg-amber-100 text-amber-800",
  INFO: "bg-sky-100 text-sky-800",
  SUCCESS: "bg-emerald-100 text-emerald-800",
};

export const SENTIMENT_STYLES: Record<ActivitySentiment, string> = {
  positive: "bg-emerald-50 text-emerald-700",
  neutral: "bg-slate-100 text-slate-600",
  negative: "bg-orange-50 text-orange-700",
  info: "bg-sky-50 text-sky-700",
};

export const ACTION_CATEGORY_LABELS: Record<string, string> = {
  MAINTENANCE: "Maintenance",
  INSPECTION: "Inspection",
  REPLACEMENT: "Replacement",
  UPGRADE: "Upgrade",
  WARRANTY: "Warranty renewal",
};

export function healthBandFromPct(pct: number): HealthBand {
  if (pct >= 90) return "EXCELLENT";
  if (pct >= 75) return "HEALTHY";
  if (pct >= 60) return "MONITOR";
  if (pct >= 45) return "WARNING";
  return "CRITICAL";
}
