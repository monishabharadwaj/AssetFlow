import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { MoreHorizontal, Pencil, Plus, Search, Trash2, Users } from "lucide-react";

import { Card, EmptyState, Skeleton } from "@/components/ui-bits";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { EmployeeFormDialog } from "@/features/employees/components/employee-form-dialog";
import { useDeactivateEmployee, useEmployees } from "@/features/employees/hooks";
import { usePermissions } from "@/features/auth/use-permissions";
import { guardRoute } from "@/lib/route-guards";
import type { Employee } from "@/lib/types/backend";
import { toast } from "@/lib/toast";

export const Route = createFileRoute("/_app/employees")({
  beforeLoad: () => guardRoute("/employees"),
  component: EmployeesPage,
});

function EmployeesPage() {
  const { can } = usePermissions();
  const canWrite = can("employees:write");
  const [q, setQ] = useState("");
  const [search, setSearch] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [editEmployee, setEditEmployee] = useState<Employee | null>(null);

  const query = useEmployees({ search: search || undefined, page_size: 50, page: 1 });
  const deactivate = useDeactivateEmployee();
  const list = query.data?.items ?? [];

  const handleDeactivate = async (e: Employee) => {
    if (!window.confirm(`Deactivate ${e.first_name} ${e.last_name}?`)) return;
    try {
      await deactivate.mutateAsync(e.id);
      toast("Employee deactivated");
    } catch (err) {
      toast((err as Error).message, "error");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Employees</h1>
          <p className="text-sm text-muted-foreground mt-1">Employee directory</p>
        </div>
        {canWrite && (
          <Button onClick={() => { setEditEmployee(null); setFormOpen(true); }} className="gap-2">
            <Plus className="size-4" /> Add employee
          </Button>
        )}
      </div>

      <Card className="p-0">
        <div className="p-4 border-b border-border relative max-w-md">
          <form onSubmit={(e) => { e.preventDefault(); setSearch(q); }}>
            <Search className="absolute left-7 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search employees…"
              className="w-full h-9 pl-9 pr-3 rounded-lg bg-background border border-border text-sm focus:outline-none focus:ring-2 focus:ring-ring/50"
            />
          </form>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground">
              <th className="px-4 py-2.5">Employee</th>
              <th className="px-4 py-2.5">Email</th>
              <th className="px-4 py-2.5">Code</th>
              <th className="px-4 py-2.5">Job title</th>
              {canWrite && <th className="px-4 py-2.5 w-12" />}
            </tr>
          </thead>
          <tbody>
            {query.isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}><td colSpan={canWrite ? 5 : 4} className="px-4 py-2.5"><Skeleton className="h-6" /></td></tr>
              ))
            ) : list.length === 0 ? (
              <tr><td colSpan={canWrite ? 5 : 4}><EmptyState title="No employees" icon={<Users className="size-5" />} /></td></tr>
            ) : list.map((e, i) => (
              <tr key={String(e.id)} className={`border-t border-border ${i % 2 === 1 ? "bg-background/20" : ""}`}>
                <td className="px-4 py-2.5 font-medium">{e.first_name} {e.last_name}</td>
                <td className="px-4 py-2.5 text-muted-foreground">{e.email}</td>
                <td className="px-4 py-2.5 text-muted-foreground">{e.employee_code}</td>
                <td className="px-4 py-2.5 text-muted-foreground">{e.job_title ?? "—"}</td>
                {canWrite && (
                  <td className="px-4 py-2.5">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="size-8"><MoreHorizontal className="size-4" /></Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => { setEditEmployee(e); setFormOpen(true); }}>
                          <Pencil className="size-3.5 mr-2" /> Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-destructive" onClick={() => void handleDeactivate(e)}>
                          <Trash2 className="size-3.5 mr-2" /> Deactivate
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <EmployeeFormDialog open={formOpen} onOpenChange={setFormOpen} employee={editEmployee} />
    </div>
  );
}
