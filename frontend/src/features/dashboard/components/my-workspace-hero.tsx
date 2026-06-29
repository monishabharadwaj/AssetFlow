import { Link } from "@tanstack/react-router";
import type { UseQueryResult } from "@tanstack/react-query";

import { Card, Pill, Skeleton } from "@/components/ui-bits";
import { glassCardClass } from "@/features/dashboard/components/dashboard-styles";
import type { MyWorkspaceResponse } from "@/lib/types/backend";
import { fmtRelative } from "@/lib/format";
import { cn } from "@/lib/utils";

export function MyWorkspaceHero({
  workspace,
  scopeLabel,
}: {
  workspace: UseQueryResult<MyWorkspaceResponse>;
  scopeLabel?: string;
}) {
  if (workspace.isLoading) {
    return (
      <section className="space-y-3">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-36 w-full rounded-xl" />
      </section>
    );
  }

  if (workspace.isError || !workspace.data) return null;

  const data = workspace.data;

  return (
    <section className="space-y-3">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <div>
          <h2 className="text-lg font-semibold">My workspace</h2>
          <p className="text-sm text-muted-foreground">
            {data.full_name} · {data.department_name}
            {scopeLabel && (
              <span className="text-foreground/70"> · {scopeLabel}</span>
            )}
          </p>
        </div>
        <Pill>{data.role}</Pill>
      </div>
      <Card className={glassCardClass()}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-1">
          <WorkspaceStat label="Assigned assets" count={data.assigned_assets.length}>
            {data.assigned_assets.length === 0 ? (
              <p className="text-sm text-muted-foreground">None assigned</p>
            ) : (
              <ul className="space-y-1 text-sm">
                {data.assigned_assets.slice(0, 4).map((a) => (
                  <li key={a.id}>
                    <Link to="/assets/$id" params={{ id: String(a.id) }} className="hover:underline">
                      {a.asset_tag} — {a.name}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </WorkspaceStat>
          <WorkspaceStat label="Upcoming maintenance" count={data.upcoming_maintenance.length}>
            {data.upcoming_maintenance.length === 0 ? (
              <p className="text-sm text-muted-foreground">None scheduled</p>
            ) : (
              <ul className="space-y-1 text-sm text-muted-foreground">
                {data.upcoming_maintenance.slice(0, 4).map((m, i) => (
                  <li key={i}>
                    <Link to="/assets/$id" params={{ id: String(m.asset_id) }} className="hover:underline">
                      {m.asset_tag}: {m.maintenance_type}{" "}
                      {m.scheduled_date ? `· ${fmtRelative(m.scheduled_date)}` : ""}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </WorkspaceStat>
          <WorkspaceStat label="Department assets" count={data.department_asset_count}>
            <p className="text-sm text-muted-foreground">Total in your department</p>
          </WorkspaceStat>
        </div>
      </Card>
    </section>
  );
}

function WorkspaceStat({
  label,
  count,
  children,
}: {
  label: string;
  count: number;
  children: React.ReactNode;
}) {
  return (
    <div className={cn("rounded-xl border border-border/80 p-4 bg-background/20")}>
      <div className="flex items-center justify-between mb-3">
        <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground">{label}</div>
        <span className="inline-flex items-center justify-center min-w-7 h-7 px-2 rounded-full bg-primary/15 text-sm font-semibold tabular-nums">
          {count}
        </span>
      </div>
      {children}
    </div>
  );
}
