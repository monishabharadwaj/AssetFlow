import type { ReactNode } from "react";

import { cn } from "../../lib/utils";

type EntityFiltersBarProps = {
  children: ReactNode;
  className?: string;
};

export function EntityFiltersBar({ children, className }: EntityFiltersBarProps) {
  return (
    <div className={cn("flex flex-wrap items-end gap-3 rounded-lg border bg-card p-4", className)}>
      {children}
    </div>
  );
}

type FilterFieldProps = {
  label: string;
  children: ReactNode;
  className?: string;
};

export function FilterField({ label, children, className }: FilterFieldProps) {
  return (
    <div className={cn("flex min-w-[140px] flex-col gap-1.5", className)}>
      <span className="text-xs font-medium text-muted-foreground">{label}</span>
      {children}
    </div>
  );
}
