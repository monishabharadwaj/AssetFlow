import type { NotificationItem } from "@/lib/types/backend";
import type { Notification } from "@/lib/types/ui";

export function mapNotification(item: NotificationItem): Notification {
  const severityMap: Record<string, Notification["severity"]> = {
    HIGH: "critical",
    MEDIUM: "warning",
    LOW: "info",
  };
  return {
    id: item.id,
    title: item.title,
    body: item.message,
    read: item.is_read,
    created_at: item.created_at,
    severity: severityMap[item.severity] ?? "info",
    asset_id: item.asset_id,
  };
}

export function mapNotifications(
  data: { items: NotificationItem[] } | NotificationItem[],
): Notification[] {
  const items = Array.isArray(data) ? data : data.items;
  return items.map(mapNotification);
}
