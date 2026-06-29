import type { ReactNode } from "react";

import { Dialog, DialogCloseButton, DialogFooter } from "../ui/dialog";
import { Button } from "../ui/button";

type FormDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: ReactNode;
  onSubmit: () => void;
  submitLabel?: string;
  isSubmitting?: boolean;
};

export function FormDialog({
  open,
  onOpenChange,
  title,
  description,
  children,
  onSubmit,
  submitLabel = "Save",
  isSubmitting,
}: FormDialogProps) {
  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
      title={title}
      description={description}
    >
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit();
        }}
      >
        <div className="space-y-4">{children}</div>
        <DialogFooter>
          <DialogCloseButton onClose={() => onOpenChange(false)} />
          <Button
            type="submit"
            disabled={isSubmitting}
            className="rounded-xl border border-blue-500/40 bg-blue-600 px-5 text-white shadow-[0_0_18px_rgba(59,130,246,0.35)] transition-all duration-300 hover:bg-blue-500 hover:shadow-[0_0_25px_rgba(59,130,246,0.55)]"
          >
            {isSubmitting ? "Saving…" : submitLabel}
          </Button>
        </DialogFooter>
      </form>
    </Dialog>
  );
}
