import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Wrench } from "lucide-react";

import { ScheduleMaintenanceSheet } from "@/features/maintenance/components/schedule-maintenance-sheet";
import { Card, EmptyState, Pill, Skeleton } from "@/components/ui-bits";
import { useMaintenanceWorkQueue } from "@/features/assets/hooks";
import { guardRoute } from "@/lib/route-guards";
import { fmtDate } from "@/lib/format";
import type { MaintenanceStatus } from "@/lib/types/backend";

export const Route = createFileRoute("/_app/maintenance")({
  beforeLoad: () => guardRoute("/maintenance"),
  component: MaintenancePage,
});

const TABS: { label: string; status: MaintenanceStatus }[] = [
  { label: "Scheduled", status: "SCHEDULED" },
  { label: "In Progress", status: "IN_PROGRESS" },
  { label: "Completed", status: "COMPLETED" },
];

function MaintenancePage() {
  const [tab, setTab] = useState<MaintenanceStatus>("SCHEDULED");
  const query = useMaintenanceWorkQueue(tab);
  const list = query.data?.items ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Maintenance</h1>
          <p className="text-sm text-muted-foreground mt-1">Track scheduled, in-progress, and completed maintenance work.</p>
        </div>
        <ScheduleMaintenanceSheet />
      </div>

      <Card className="p-0">
        <div className="p-4 border-b border-border flex items-center gap-1">
          {TABS.map((t) => (
            <button
              key={t.status}
              type="button"
              onClick={() => setTab(t.status)}
              className={`px-3 h-8 rounded-md text-sm ${tab === t.status ? "bg-accent text-foreground" : "text-muted-foreground hover:text-foreground"}`}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground">
                <th className="px-4 py-2.5">Tag</th>
                <th className="px-4 py-2.5">Asset</th>
                <th className="px-4 py-2.5">Type</th>
                <th className="px-4 py-2.5">Status</th>
                <th className="px-4 py-2.5">Scheduled</th>
                <th className="px-4 py-2.5">Description</th>
              </tr>
            </thead>
            <tbody>
              {query.isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}><td colSpan={6} className="px-4 py-2.5"><Skeleton className="h-6" /></td></tr>
                ))
              ) : list.length === 0 ? (
                <tr>
                  <td colSpan={6}>
                    <EmptyState title="Nothing in this queue" icon={<Wrench className="size-5" />} />
                  </td>
                </tr>
              ) : list.map((item, i) => (
                <tr key={item.record.id} className={`border-t border-border hover:bg-accent/20 ${i % 2 === 1 ? "bg-background/20" : ""}`}>
                  <td className="px-4 py-2.5 font-mono text-xs">
                    <Link to="/assets/$id" params={{ id: String(item.asset_id) }} className="hover:underline">
                      {item.asset_tag}
                    </Link>
                  </td>
                  <td className="px-4 py-2.5">{item.asset_name}</td>
                  <td className="px-4 py-2.5 text-muted-foreground">{item.record.maintenance_type.replace(/_/g, " ")}</td>
                  <td className="px-4 py-2.5">
                    <Pill>{item.record.status.replace(/_/g, " ")}</Pill>
                  </td>
                  <td className="px-4 py-2.5 text-muted-foreground">{fmtDate(item.record.scheduled_date)}</td>
                  <td className="px-4 py-2.5 text-muted-foreground max-w-xs truncate">{item.record.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
