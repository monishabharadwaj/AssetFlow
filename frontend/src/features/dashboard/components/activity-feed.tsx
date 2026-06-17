import { ArrowRightLeft, UserCheck, Wrench } from "lucide-react";
import { Link } from "react-router-dom";

import { EmptyState } from "../../../shared/components/feedback/empty-state";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
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

function formatActivityTitle(activityType: string): string {
  if (activityType.startsWith("ALLOCATION_")) {
    return activityType.replace("ALLOCATION_", "").toLowerCase();
  }
  return activityType.toLowerCase();
}

export function ActivityFeed({ activities }: ActivityFeedProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Latest allocation, transfer, and maintenance events</CardDescription>
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
              return (
                <div key={`${activity.activity_type}-${activity.occurred_at}-${index}`}>
                  <Link
                    to={`/assets/${activity.asset_id}`}
                    className="flex items-start gap-3 rounded-lg p-3 transition-colors hover:bg-accent"
                  >
                    <div className="mt-0.5 rounded-md bg-primary/10 p-2">
                      <Icon className="h-4 w-4 text-primary" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium capitalize text-foreground">
                        {formatActivityTitle(activity.activity_type)}
                      </p>
                      <p className="mt-0.5 line-clamp-2 text-sm text-muted-foreground">
                        {activity.message}
                      </p>
                      <p
                        className="mt-1 text-xs text-muted-foreground"
                        title={formatDateTime(activity.occurred_at)}
                      >
                        {formatRelativeTime(activity.occurred_at)}
                      </p>
                    </div>
                  </Link>
                  {index < activities.length - 1 ? <Separator /> : null}
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
