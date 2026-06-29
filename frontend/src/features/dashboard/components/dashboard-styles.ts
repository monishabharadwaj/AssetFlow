import { cn } from "@/lib/utils";

/** Premium glass card styling for dashboard sections */
export function glassCardClass(extra?: string) {
  return cn(
    "rounded-xl border border-white/8 bg-card/60 backdrop-blur-sm",
    "shadow-[0_4px_24px_rgba(0,0,0,0.25)]",
    extra,
  );
}
