import { Badge } from "../ui/badge";
import { formatStatusLabel, STATUS_BADGE_CLASSES } from "../../lib/status-colors";
import { cn } from "../../lib/utils";

type StatusBadgeProps = {
  status: string;
  className?: string;
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <Badge
      variant="secondary"
      className={cn("border font-medium", STATUS_BADGE_CLASSES[status] ?? "", className)}
    >
      {formatStatusLabel(status)}
    </Badge>
  );
}
