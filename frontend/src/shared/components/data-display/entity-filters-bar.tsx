import type { ReactNode } from "react";

import { cn } from "../../lib/utils";

type EntityFiltersBarProps = {
  children: ReactNode;
  className?: string;
};

export function EntityFiltersBar({
  children,
  className,
}: EntityFiltersBarProps) {
  return (
    <div
      className={cn(
        "rounded-3xl border border-slate-700 bg-[#111827] p-5",
        "shadow-[0_0_20px_rgba(59,130,246,0.12)]",
        "flex flex-wrap items-end gap-5",
        className,
      )}
    >
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
    <div className={cn("flex min-w-[170px] flex-col gap-2", className)}>
      <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        {label}
      </span>
      {children}
    </div>
  );
}
