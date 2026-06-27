import { AlertTriangle, Laptop, Sparkles, Wrench } from "lucide-react";
import { Link } from "react-router-dom";

import type { DashboardSummary } from "../../../shared/api/types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../shared/components/ui/card";
import { cn } from "../../../shared/lib/utils";

type AttentionQueueProps = {
  items: DashboardSummary["attention_items"];
};

const PRIORITY_CLASSES: Record<string, string> = {
  HIGH: "border-red-500/30 bg-red-500/10 hover:border-red-400 hover:shadow-[0_0_18px_rgba(239,68,68,0.30)]",

  MEDIUM:
    "border-amber-500/30 bg-amber-500/10 hover:border-amber-400 hover:shadow-[0_0_18px_rgba(245,158,11,0.30)]",

  LOW: "border-blue-500/30 bg-blue-500/10 hover:border-blue-400 hover:shadow-[0_0_18px_rgba(59,130,246,0.30)]",
};

function itemIcon(type: string) {
  if (type === "HIGH_RISK") return Sparkles;
  if (type === "MAINTENANCE_DUE") return Wrench;
  if (type === "IN_MAINTENANCE") return AlertTriangle;
  return Laptop;
}

export function AttentionQueue({ items }: AttentionQueueProps) {
  return (
    <Card className="h-full rounded-2xl border border-slate-700 bg-[#111827] shadow-[0_0_30px_rgba(59,130,246,0.08)]">
      <CardHeader>
        <CardTitle className="text-xl font-semibold text-white">
          Needs Attention
        </CardTitle>
        <CardDescription className="text-slate-400">
          Prioritized by urgency
        </CardDescription>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <p className="py-6 text-center text-sm text-muted-foreground">
            No items need attention.
          </p>
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
                    "flex items-start gap-3 rounded-xl border p-4 transition-all duration-300",
                    PRIORITY_CLASSES[item.priority] ?? "",
                  )}
                >
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-800">
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium">{headline}</p>
                    <p className="text-xs text-muted-foreground">
                      {item.message}
                    </p>
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
