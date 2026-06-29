import { useState } from "react";
import { Link } from "react-router-dom";
import { Bell, CheckCheck } from "lucide-react";

import { Button } from "../../../shared/components/ui/button";
import { Sheet } from "../../../shared/components/ui/sheet";
import {
  useMarkAllNotificationsRead,
  useMarkNotificationRead,
  useNotifications,
} from "../hooks/use-operations";
import type { NotificationItem } from "../api/operations-api";

const SEVERITY_CLASSES: Record<string, string> = {
  HIGH: "border-orange-500/30 bg-orange-500/10",
  MEDIUM: "border-amber-500/30 bg-amber-500/10",
  LOW: "border-sky-500/30 bg-sky-500/10",
  INFO: "border-sky-500/30 bg-sky-500/10",
  SUCCESS: "border-emerald-500/30 bg-emerald-500/10",
};

type NotificationListProps = {
  items: NotificationItem[];
  onMarkRead: (id: string) => void;
  compact?: boolean;
};

export function NotificationList({ items, onMarkRead, compact = false }: NotificationListProps) {
  if (items.length === 0) {
    return (
      <p className="py-4 text-center text-sm text-muted-foreground">
        No notifications yet. Run AI scoring to generate alerts.
      </p>
    );
  }

  return (
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
          {!compact ? <p className="mt-1 text-xs text-muted-foreground">{item.message}</p> : null}
          <div className="mt-2 flex flex-wrap gap-2">
            {item.asset_id ? (
              <Link
                to={`/assets/${item.asset_id}`}
                className="text-xs font-medium text-primary hover:underline"
                onClick={() => {
                  if (!item.is_read) onMarkRead(item.id);
                }}
              >
                View asset →
              </Link>
            ) : null}
            {!item.is_read ? (
              <button
                type="button"
                className="text-xs text-muted-foreground hover:text-foreground"
                onClick={() => onMarkRead(item.id)}
              >
                Mark read
              </button>
            ) : null}
          </div>
        </div>
      ))}
    </div>
  );
}

export function NotificationsBell() {
  const [open, setOpen] = useState(false);
  const { data } = useNotifications(20);
  const markRead = useMarkNotificationRead();
  const markAll = useMarkAllNotificationsRead();

  const unread = data?.unread_count ?? 0;
  const items = data?.items ?? [];

  return (
    <>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="relative"
        onClick={() => setOpen(true)}
        aria-label="Notifications"
      >
        <Bell className="h-4 w-4" />
        {unread > 0 ? (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-orange-500 px-1 text-[10px] font-medium text-white">
            {unread > 99 ? "99+" : unread}
          </span>
        ) : null}
      </Button>
      <Sheet
        open={open}
        onOpenChange={setOpen}
        title="Notifications"
        description="AI escalations, warranty alerts, and policy automation for your scope"
      >
        {unread > 0 ? (
          <div className="mb-4 flex justify-end">
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
          </div>
        ) : null}
        <NotificationList items={items} onMarkRead={(id) => void markRead.mutateAsync(id)} />
      </Sheet>
    </>
  );
}
