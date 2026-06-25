import type { LucideIcon } from "lucide-react";
import { ArrowRightLeft, HeartPulse, UserCheck, Wrench } from "lucide-react";

import { formatDateTime, formatRelativeTime } from "../../lib/date";

type TimelineEventItemProps = {
  eventType: string;
  title: string;
  occurredAt: string;
  details?: Record<string, unknown>;
};

const HIDDEN_DETAIL_KEYS = new Set(["action", "health_score"]);

const DETAIL_LABELS: Record<string, string> = {
  employee: "Employee",
  from_department: "From",
  to_department: "To",
  from_location: "From location",
  to_location: "To location",
  reason: "Reason",
  type: "Type",
  status: "Status",
  scheduled_date: "Scheduled",
  completed_date: "Completed",
  cost: "Cost",
  description: "Description",
  summary: "Summary",
  condition_rating: "Condition",
  failure_count: "Failures",
  returned_at: "Returned",
  notes: "Notes",
};

function getEventIcon(eventType: string): LucideIcon {
  if (eventType.includes("ALLOCATION") || eventType.includes("ASSIGN")) return UserCheck;
  if (eventType.includes("TRANSFER")) return ArrowRightLeft;
  if (eventType.includes("MAINTENANCE")) return Wrench;
  if (eventType.includes("HEALTH")) return HeartPulse;
  return UserCheck;
}

function formatDetailValue(key: string, value: unknown): string {
  if (key === "cost" && typeof value === "number") {
    return `$${value.toFixed(2)}`;
  }
  if (key === "summary" || key === "description" || key === "reason" || key === "notes") {
    return String(value);
  }
  return String(value);
}

export function TimelineEventItem({ eventType, title, occurredAt, details }: TimelineEventItemProps) {
  const Icon = getEventIcon(eventType);
  const detailEntries = details
    ? Object.entries(details).filter(
        ([key, value]) => !HIDDEN_DETAIL_KEYS.has(key) && value != null && value !== "",
      )
    : [];

  const summary = details?.summary as string | undefined;
  const visibleEntries = summary
    ? detailEntries.filter(([key]) => key !== "summary")
    : detailEntries;

  return (
    <div className="flex gap-3 rounded-lg border p-3">
      <div className="mt-0.5 rounded-md bg-primary/10 p-2">
        <Icon className="h-4 w-4 text-primary" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium">{title}</p>
        {summary ? <p className="mt-1 text-sm text-muted-foreground">{summary}</p> : null}
        {visibleEntries.length > 0 ? (
          <dl className="mt-2 grid gap-1 text-xs text-muted-foreground">
            {visibleEntries.slice(0, 5).map(([key, value]) => (
              <div key={key} className="flex gap-2">
                <dt className="shrink-0 font-medium">{DETAIL_LABELS[key] ?? key.replace(/_/g, " ")}:</dt>
                <dd className="min-w-0">{formatDetailValue(key, value)}</dd>
              </div>
            ))}
          </dl>
        ) : null}
        <p className="mt-1 text-xs text-muted-foreground" title={formatDateTime(occurredAt)}>
          {formatRelativeTime(occurredAt)}
        </p>
      </div>
    </div>
  );
}

export function groupTimelineByDay<T extends { occurred_at: string }>(items: T[]): Array<{ day: string; items: T[] }> {
  const groups = new Map<string, T[]>();
  for (const item of items) {
    const dayKey = new Date(item.occurred_at).toDateString();
    const existing = groups.get(dayKey) ?? [];
    existing.push(item);
    groups.set(dayKey, existing);
  }
  return Array.from(groups.entries()).map(([, dayItems]) => ({
    day: dayItems[0]!.occurred_at,
    items: dayItems,
  }));
}
