import { Dialog, DialogCloseButton, DialogFooter } from "../ui/dialog";
import { Button } from "../ui/button";

type ConfirmDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  confirmLabel?: string;
  onConfirm: () => void;
  isConfirming?: boolean;
  destructive?: boolean;
};

export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmLabel = "Confirm",
  onConfirm,
  isConfirming,
  destructive,
}: ConfirmDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange} title={title} description={description}>
      <DialogFooter>
        <DialogCloseButton onClose={() => onOpenChange(false)} />
        <Button
          type="button"
          variant={destructive ? "default" : "secondary"}
          className={destructive ? "bg-destructive text-destructive-foreground hover:opacity-90" : undefined}
          disabled={isConfirming}
          onClick={onConfirm}
        >
          {isConfirming ? "Processing…" : confirmLabel}
        </Button>
      </DialogFooter>
    </Dialog>
  );
}
