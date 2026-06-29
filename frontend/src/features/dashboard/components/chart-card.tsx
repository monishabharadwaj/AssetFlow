import type { ReactNode } from "react";
import { BarChart3 } from "lucide-react";

import { Card, CardHeader, EmptyState } from "@/components/ui-bits";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import { cn } from "@/lib/utils";

export function ChartCard({
  title,
  subtitle,
  data,
  emptyTitle,
  emptyHint,
  heightClass = "h-52",
  children,
  className,
}: {
  title: string;
  subtitle?: string;
  data?: unknown[];
  emptyTitle?: string;
  emptyHint?: string;
  heightClass?: string;
  children: ReactNode;
  className?: string;
}) {
  const hasData = data && data.length > 0;
  return (
    <Card className={cn(glassCardClass(), className)}>
      <CardHeader title={title} subtitle={subtitle} />
      <div className={heightClass}>
        {hasData ? children : (
          <EmptyState
            title={emptyTitle ?? "No data"}
            hint={emptyHint}
            icon={<BarChart3 className="size-5" />}
          />
        )}
      </div>
    </Card>
  );
}
