import * as React from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";

import { cn } from "../../lib/utils";
import { Button } from "./button";

type SheetProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  side?: "right" | "bottom";
};

export function Sheet({
  open,
  onOpenChange,
  title,
  description,
  children,
  side = "right",
}: SheetProps) {
  React.useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onOpenChange(false);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onOpenChange]);

  if (!open) return null;

  return createPortal(
    <div className="fixed inset-0 z-50">
      <div
        className="fixed inset-0 bg-black/70 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />
      <div
        className={cn(
          "fixed z-50 flex flex-col rounded-l-3xl border border-slate-700 bg-[#111827] text-white shadow-[0_0_35px_rgba(59,130,246,0.18)]",
          side === "right" && "inset-y-0 right-0 h-full w-full max-w-md",
          side === "bottom" &&
            "inset-x-0 bottom-0 max-h-[90vh] w-full rounded-t-lg",
        )}
        role="dialog"
        aria-modal="true"
      >
        <div className="flex items-start justify-between border-b border-slate-700 px-6 py-5">
          <div>
            <h2 className="text-xl font-bold text-white">{title}</h2>
            {description ? (
              <p className="mt-1 text-sm text-slate-400">{description}</p>
            ) : null}
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => onOpenChange(false)}
            className="rounded-xl text-slate-400 transition-all duration-300 hover:bg-blue-500/20 hover:text-white hover:shadow-[0_0_18px_rgba(59,130,246,0.45)]"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-4">{children}</div>
      </div>
    </div>,
    document.body,
  );
}
