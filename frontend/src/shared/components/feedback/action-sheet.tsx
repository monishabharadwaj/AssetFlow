import { Sheet } from "../ui/sheet";

type ActionSheetProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string;
  children: React.ReactNode;
};

export function ActionSheet({ open, onOpenChange, title, description, children }: ActionSheetProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange} title={title} description={description}>
      {children}
    </Sheet>
  );
}
