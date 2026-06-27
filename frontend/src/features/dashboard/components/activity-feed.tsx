import { ArrowRightLeft, UserCheck, Wrench } from "lucide-react";
import { Link } from "react-router-dom";

import { EmptyState } from "../../../shared/components/feedback/empty-state";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../shared/components/ui/card";
import { Separator } from "../../../shared/components/ui/separator";
import { formatDateTime, formatRelativeTime } from "../../../shared/lib/date";
import type { DashboardSummary } from "../../../shared/api/types";

type ActivityFeedProps = {
  activities: DashboardSummary["recent_activity"];
};

function getActivityIcon(activityType: string) {
  if (activityType.startsWith("ALLOCATION")) {
    return UserCheck;
  }
  if (activityType === "TRANSFER") {
    return ArrowRightLeft;
  }
  if (activityType === "MAINTENANCE") {
    return Wrench;
  }
  return UserCheck;
}

export function ActivityFeed({ activities }: ActivityFeedProps) {
  return (
    <Card className="h-full rounded-2xl border border-slate-700 bg-[#111827] shadow-[0_0_25px_rgba(59,130,246,0.08)]">
      <CardHeader>
        <CardTitle>What just happened</CardTitle>
        <CardDescription className="text-slate-400">
          Latest operations across all assets
        </CardDescription>
      </CardHeader>
      <CardContent>
        {activities.length === 0 ? (
          <EmptyState
            title="No recent activity"
            description="Lifecycle events will appear here as assets are assigned, transferred, or maintained."
          />
        ) : (
          <div className="space-y-0">
            {activities.map((activity, index) => {
              const Icon = getActivityIcon(activity.activity_type);
              const headline = activity.headline || activity.message;
              return (
                <div
                  key={`${activity.activity_type}-${activity.occurred_at}-${index}`}
                >
                  <Link
                    to={`/assets/${activity.asset_id}?tab=timeline`}
                    className="flex items-start gap-3 rounded-xl border border-transparent p-4 transition-all duration-300 hover:border-blue-500/30 hover:bg-slate-800/70 hover:shadow-[0_0_18px_rgba(59,130,246,0.20)]"
                  >
                    <div className="mt-0.5 flex h-11 w-11 items-center justify-center rounded-xl bg-slate-800 shadow-[0_0_15px_rgba(59,130,246,0.15)]">
                      <Icon className="h-5 w-5 text-blue-400" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-white">
                        {headline}
                      </p>
                      <p className="mt-1 line-clamp-2 text-sm text-slate-400">
                        {activity.message}
                      </p>
                      <p
                        className="mt-2 text-xs font-medium text-slate-500"
                        title={formatDateTime(activity.occurred_at)}
                      >
                        {activity.asset_tag ? `${activity.asset_tag} · ` : ""}
                        {formatRelativeTime(activity.occurred_at)}
                      </p>
                    </div>
                  </Link>
                  {index < activities.length - 1 ? (
                    <Separator className="bg-slate-800" />
                  ) : null}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
