import type { AssetStatus } from "../../api/types";
import { cn } from "../../lib/utils";
import { formatStatusLabel } from "../../lib/status-colors";

const LIFECYCLE_STEPS = ["AVAILABLE", "ASSIGNED", "IN_MAINTENANCE", "RETURNED"] as const;

const STATUS_ACTIVE_INDEX: Record<AssetStatus, number> = {
  AVAILABLE: 0,
  ASSIGNED: 1,
  IN_MAINTENANCE: 2,
  RETIRED: 3,
  DISPOSED: 3,
};

type LifecycleProgressStripProps = {
  status: AssetStatus;
  compact?: boolean;
};

function stepLabel(step: (typeof LIFECYCLE_STEPS)[number]): string {
  if (step === "RETURNED") return "Returned";
  return formatStatusLabel(step);
}

export function LifecycleProgressStrip({ status, compact = false }: LifecycleProgressStripProps) {
  const activeIndex = STATUS_ACTIVE_INDEX[status] ?? 0;
  const returnedComplete = status === "AVAILABLE" && activeIndex === 0;

  return (
    <div className={cn("w-full", compact ? "space-y-1" : "space-y-2")}>
      <div className="flex items-center gap-1">
        {LIFECYCLE_STEPS.map((step, index) => {
          const isActive = index === activeIndex;
          const isComplete =
            index < activeIndex || (step === "RETURNED" && returnedComplete && index === 3);
          return (
            <div key={step} className="flex flex-1 items-center gap-1">
              <div
                className={cn(
                  "flex h-2 flex-1 rounded-full transition-colors",
                  isActive ? "bg-primary" : isComplete ? "bg-primary/40" : "bg-muted",
                )}
              />
            </div>
          );
        })}
      </div>
      {!compact ? (
        <div className="flex justify-between gap-1 text-[10px] text-muted-foreground sm:text-xs">
          {LIFECYCLE_STEPS.map((step, index) => (
            <span
              key={step}
              className={cn(
                "flex-1 text-center",
                index === activeIndex ? "font-medium text-foreground" : "",
              )}
            >
              {stepLabel(step)}
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}
