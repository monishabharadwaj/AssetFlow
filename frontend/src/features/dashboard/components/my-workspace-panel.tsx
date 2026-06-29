import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Bell, Calendar, Laptop } from "lucide-react";

import { fetchMyWorkspace } from "../../auth/api";
import { useAuth } from "../../auth/auth-context";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { formatDate } from "../../../shared/lib/format";

export function MyWorkspacePanel() {
  const { user } = useAuth();
  const { data, isLoading } = useQuery({
    queryKey: ["dashboard", "my-workspace"],
    queryFn: fetchMyWorkspace,
  });

  if (isLoading || !data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>My Workspace</CardTitle>
          <CardDescription>Loading your assigned assets…</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  const scopeLabel =
    user?.role === "ADMIN"
      ? "Organization-wide view"
      : `${data.department_name} department`;

  return (
    <Card>
      <CardHeader>
        <CardTitle>My Workspace</CardTitle>
        <CardDescription>
          Welcome back, {data.full_name}. {scopeLabel} · {data.department_asset_count} department assets
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-6 lg:grid-cols-3">
        <section className="space-y-3">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Laptop className="h-4 w-4" />
            My assigned assets
          </h3>
          {data.assigned_assets.length === 0 ? (
            <p className="text-sm text-muted-foreground">No assets currently assigned to you.</p>
          ) : (
            <ul className="space-y-2">
              {data.assigned_assets.map((asset) => (
                <li key={asset.id} className="rounded-lg border p-3 text-sm">
                  <Link to={`/assets/${asset.id}`} className="font-medium text-primary hover:underline">
                    {asset.asset_tag}
                  </Link>
                  <p>{asset.name}</p>
                  <p className="text-muted-foreground">
                    {asset.asset_type_name ?? "Asset"} · {asset.current_status.replace(/_/g, " ")}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </section>
        <section className="space-y-3">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Calendar className="h-4 w-4" />
            Upcoming maintenance
          </h3>
          {data.upcoming_maintenance.length === 0 ? (
            <p className="text-sm text-muted-foreground">No scheduled maintenance on your assets.</p>
          ) : (
            <ul className="space-y-2">
              {data.upcoming_maintenance.map((item) => (
                <li key={`${item.asset_id}-${item.scheduled_date}`} className="rounded-lg border p-3 text-sm">
                  <Link to={`/assets/${item.asset_id}?tab=maintenance`} className="font-medium text-primary hover:underline">
                    {item.asset_tag}
                  </Link>
                  <p>{item.maintenance_type.replace(/_/g, " ")} · {item.status.replace(/_/g, " ")}</p>
                  <p className="text-muted-foreground">{formatDate(item.scheduled_date)}</p>
                </li>
              ))}
            </ul>
          )}
        </section>
        <section className="space-y-3">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <Bell className="h-4 w-4" />
            My notifications
          </h3>
          {data.notifications.length === 0 ? (
            <p className="text-sm text-muted-foreground">No notifications for your assigned assets.</p>
          ) : (
            <ul className="space-y-2">
              {data.notifications.map((item) => (
                <li key={item.id} className="rounded-lg border p-3 text-sm">
                  <p className="font-medium">{item.title}</p>
                  <p className="text-muted-foreground">{item.message}</p>
                </li>
              ))}
            </ul>
          )}
        </section>
      </CardContent>
    </Card>
  );
}
