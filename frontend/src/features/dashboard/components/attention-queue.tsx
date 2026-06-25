import { AlertTriangle, Laptop, Sparkles, Wrench } from "lucide-react";
import { Link } from "react-router-dom";

import type { DashboardSummary } from "../../../shared/api/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { cn } from "../../../shared/lib/utils";

type AttentionQueueProps = {
  items: DashboardSummary["attention_items"];
};

const PRIORITY_CLASSES: Record<string, string> = {
  HIGH: "border-rose-200 bg-rose-50/50",
  MEDIUM: "border-amber-200 bg-amber-50/50",
  LOW: "border-sky-200 bg-sky-50/50",
};

function itemIcon(type: string) {
  if (type === "HIGH_RISK") return Sparkles;
  if (type === "MAINTENANCE_DUE") return Wrench;
  if (type === "IN_MAINTENANCE") return AlertTriangle;
  return Laptop;
}

export function AttentionQueue({ items }: AttentionQueueProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Needs attention</CardTitle>
        <CardDescription>Actionable items routed to asset stories</CardDescription>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">No items need attention.</p>
        ) : (
          <div className="space-y-2">
            {items.map((item) => {
              const Icon = itemIcon(item.item_type);
              const headline = item.headline || item.asset_tag;
              return (
                <Link
                  key={`${item.item_type}-${item.asset_id}`}
                  to={`/assets/${item.asset_id}`}
                  className={cn(
                    "flex items-start gap-3 rounded-lg border p-3 transition-colors hover:opacity-90",
                    PRIORITY_CLASSES[item.priority] ?? "",
                  )}
                >
                  <Icon className="mt-0.5 h-4 w-4 shrink-0" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium">{headline}</p>
                    <p className="text-xs text-muted-foreground">{item.message}</p>
                  </div>
                  <span className="ml-auto shrink-0 text-xs font-medium uppercase text-muted-foreground">
                    {item.priority}
                  </span>
                </Link>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
