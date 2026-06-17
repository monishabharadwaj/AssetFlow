import type { LucideIcon } from "lucide-react";
import { ArrowRightLeft, HeartPulse, UserCheck, Wrench } from "lucide-react";

import { formatDateTime, formatRelativeTime } from "../../lib/date";

type TimelineEventItemProps = {
  eventType: string;
  title: string;
  occurredAt: string;
  details?: Record<string, unknown>;
};

function getEventIcon(eventType: string): LucideIcon {
  if (eventType.includes("ALLOCATION") || eventType.includes("ASSIGN")) return UserCheck;
  if (eventType.includes("TRANSFER")) return ArrowRightLeft;
  if (eventType.includes("MAINTENANCE")) return Wrench;
  if (eventType.includes("HEALTH")) return HeartPulse;
  return UserCheck;
}

export function TimelineEventItem({ eventType, title, occurredAt, details }: TimelineEventItemProps) {
  const Icon = getEventIcon(eventType);
  const detailEntries = details ? Object.entries(details).filter(([, v]) => v != null && v !== "") : [];

  return (
    <div className="flex gap-3 rounded-lg border p-3">
      <div className="mt-0.5 rounded-md bg-primary/10 p-2">
        <Icon className="h-4 w-4 text-primary" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium">{title}</p>
        {detailEntries.length > 0 ? (
          <dl className="mt-2 grid gap-1 text-xs text-muted-foreground">
            {detailEntries.slice(0, 4).map(([key, value]) => (
              <div key={key} className="flex gap-2">
                <dt className="font-medium capitalize">{key.replace(/_/g, " ")}:</dt>
                <dd className="truncate">{String(value)}</dd>
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
