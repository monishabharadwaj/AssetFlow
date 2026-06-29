import * as React from "react";
import { createPortal } from "react-dom";

import { cn } from "../../lib/utils";
import { Button } from "./button";

type DialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
};

export function Dialog({
  open,
  onOpenChange,
  title,
  description,
  children,
  className,
}: DialogProps) {
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
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black/70 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />
      <div
        className={cn(
          "relative z-50 w-full max-w-xl rounded-3xl border border-slate-700 bg-[#111827] p-7 text-white shadow-[0_0_35px_rgba(59,130,246,0.18)]",
          className,
        )}
        role="dialog"
        aria-modal="true"
      >
        <div className="mb-6 border-b border-slate-700 pb-4">
          <h2 className="text-2xl font-bold text-white">{title}</h2>
          {description ? (
            <p className="mt-2 text-sm text-slate-400">{description}</p>
          ) : null}
        </div>
        {children}
      </div>
    </div>,
    document.body,
  );
}

export function DialogFooter({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        "mt-8 border-t border-slate-700 pt-5 flex justify-end gap-3",
        className,
      )}
    >
      {children}
    </div>
  );
}

export function DialogCloseButton({
  onClose,
  label = "Cancel",
}: {
  onClose: () => void;
  label?: string;
}) {
  return (
    <Button
      type="button"
      variant="ghost"
      onClick={onClose}
      className="rounded-xl border border-slate-700 text-slate-300 transition-all duration-300 hover:border-blue-500/40 hover:bg-blue-500/10 hover:text-white"
    >
      {label}
    </Button>
  );
}
