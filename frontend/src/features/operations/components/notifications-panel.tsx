import { Link } from "react-router-dom";
import { Bell, CheckCheck } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { Button } from "../../../shared/components/ui/button";
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from "../hooks/use-operations";
import { NotificationList } from "./notifications-bell";

export function NotificationsPanel() {
  const { data, isLoading } = useNotifications(8);
  const markAll = useMarkAllNotificationsRead();
  const markRead = useMarkNotificationRead();

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
        ) : (
          <>
            <NotificationList
              items={items}
              onMarkRead={(id) => void markRead.mutateAsync(id)}
            />
            {items.length > 0 ? (
              <Link to="/reports" className="mt-4 inline-block text-sm font-medium text-primary hover:underline">
                View all reports →
              </Link>
            ) : null}
          </>
        )}
      </CardContent>
    </Card>
  );
}
