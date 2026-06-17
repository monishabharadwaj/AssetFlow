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
    <Dialog open={open} onOpenChange={onOpenChange} title={title} description={description}>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit();
        }}
      >
        <div className="space-y-4">{children}</div>
        <DialogFooter>
          <DialogCloseButton onClose={() => onOpenChange(false)} />
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Saving…" : submitLabel}
          </Button>
        </DialogFooter>
      </form>
    </Dialog>
  );
}
