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

export function Dialog({ open, onOpenChange, title, description, children, className }: DialogProps) {
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
      <div className="fixed inset-0 bg-black/50" onClick={() => onOpenChange(false)} />
      <div
        className={cn(
          "relative z-50 w-full max-w-lg rounded-lg border bg-card p-6 shadow-lg",
          className,
        )}
        role="dialog"
        aria-modal="true"
      >
        <div className="mb-4">
          <h2 className="text-lg font-semibold">{title}</h2>
          {description ? <p className="mt-1 text-sm text-muted-foreground">{description}</p> : null}
        </div>
        {children}
      </div>
    </div>,
    document.body,
  );
}

export function DialogFooter({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("mt-6 flex justify-end gap-2", className)}>{children}</div>;
}

export function DialogCloseButton({ onClose, label = "Cancel" }: { onClose: () => void; label?: string }) {
  return (
    <Button type="button" variant="ghost" onClick={onClose}>
      {label}
    </Button>
  );
}
