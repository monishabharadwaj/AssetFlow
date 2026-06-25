import type { LucideIcon } from "lucide-react";
import {
  Car,
  Laptop,
  Monitor,
  Package,
  Printer,
  Server,
  Smartphone,
  Wrench,
} from "lucide-react";

import { cn } from "../../lib/utils";

const TYPE_ICONS: Record<string, LucideIcon> = {
  Laptop: Laptop,
  "Desktop Workstation": Monitor,
  Server: Server,
  Printer: Printer,
  Smartphone: Smartphone,
  Vehicle: Car,
  Van: Car,
};

type AssetTypeIconProps = {
  typeName?: string | null;
  className?: string;
  iconClassName?: string;
};

export function AssetTypeIcon({ typeName, className, iconClassName }: AssetTypeIconProps) {
  const Icon = (typeName && TYPE_ICONS[typeName]) || Package;
  return (
    <div
      className={cn(
        "flex h-16 w-16 items-center justify-center rounded-xl bg-primary/10 text-primary",
        className,
      )}
    >
      <Icon className={cn("h-8 w-8", iconClassName)} />
    </div>
  );
}

export function getAssetTypeIcon(typeName?: string | null): LucideIcon {
  if (typeName && TYPE_ICONS[typeName]) return TYPE_ICONS[typeName];
  return Wrench;
}
