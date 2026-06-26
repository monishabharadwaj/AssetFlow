import { Link } from "react-router-dom";
import { Bell, CheckCheck } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { Button } from "../../../shared/components/ui/button";
import { useMarkAllNotificationsRead, useNotifications } from "../hooks/use-operations";

const SEVERITY_CLASSES: Record<string, string> = {
  HIGH: "border-orange-500/30 bg-orange-500/10",
  MEDIUM: "border-amber-500/30 bg-amber-500/10",
  LOW: "border-sky-500/30 bg-sky-500/10",
  INFO: "border-sky-500/30 bg-sky-500/10",
  SUCCESS: "border-emerald-500/30 bg-emerald-500/10",
};

export function NotificationsPanel() {
  const { data, isLoading } = useNotifications(8);
  const markAll = useMarkAllNotificationsRead();

  const items = data?.items ?? [];
  const unread = data?.unread_count ?? 0;

  return (
    <Card className="glass-card border-border/60">
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Smart notifications
            {unread > 0 ? (
              <span className="rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-800">
                {unread} new
              </span>
            ) : null}
          </CardTitle>
          <CardDescription>AI escalations, warranty alerts, and policy automation</CardDescription>
        </div>
        {unread > 0 ? (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={markAll.isPending}
            onClick={() => void markAll.mutateAsync()}
          >
            <CheckCheck className="mr-1 h-4 w-4" />
            Mark all read
          </Button>
        ) : null}
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p className="text-sm text-muted-foreground">Loading notifications…</p>
        ) : items.length === 0 ? (
          <p className="py-4 text-center text-sm text-muted-foreground">
            No notifications yet. Run the AI pipeline to generate escalations.
          </p>
        ) : (
          <div className="space-y-2">
            {items.map((item) => (
              <div
                key={item.id}
                className={`rounded-lg border p-3 text-sm ${SEVERITY_CLASSES[item.severity] ?? ""} ${item.is_read ? "opacity-70" : ""}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="font-medium">{item.title}</p>
                  <span className="shrink-0 text-xs uppercase text-muted-foreground">{item.severity}</span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{item.message}</p>
                {item.asset_id ? (
                  <Link
                    to={`/assets/${item.asset_id}`}
                    className="mt-2 inline-block text-xs font-medium text-primary hover:underline"
                  >
                    View asset →
                  </Link>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
