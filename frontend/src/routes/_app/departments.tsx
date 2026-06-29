import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Building2, MoreHorizontal, Pencil, Plus, Trash2 } from "lucide-react";

import { Card, EmptyState, Skeleton } from "@/components/ui-bits";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { DepartmentFormDialog } from "@/features/departments/components/department-form-dialog";
import { useDeactivateDepartment, useDepartments } from "@/features/departments/hooks";
import { usePermissions } from "@/features/auth/use-permissions";
import { guardRoute } from "@/lib/route-guards";
import type { Department } from "@/lib/types/backend";
import { toast } from "@/lib/toast";

export const Route = createFileRoute("/_app/departments")({
  beforeLoad: () => guardRoute("/departments"),
  component: DepartmentsPage,
});

function DepartmentsPage() {
  const { can } = usePermissions();
  const canWrite = can("departments:write");
  const query = useDepartments({ page: 1, page_size: 100 });
  const deactivate = useDeactivateDepartment();
  const [formOpen, setFormOpen] = useState(false);
  const [editDept, setEditDept] = useState<Department | null>(null);
  const list = query.data?.items ?? [];

  const handleDeactivate = async (d: Department) => {
    if (!window.confirm(`Deactivate ${d.name}?`)) return;
    try {
      await deactivate.mutateAsync(d.id);
      toast("Department deactivated");
    } catch (err) {
      toast((err as Error).message, "error");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Departments</h1>
          <p className="text-sm text-muted-foreground mt-1">Organizational departments</p>
        </div>
        {canWrite && (
          <Button onClick={() => { setEditDept(null); setFormOpen(true); }} className="gap-2">
            <Plus className="size-4" /> Add department
          </Button>
        )}
      </div>

      <Card className="p-0">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-[11px] uppercase tracking-wider text-muted-foreground">
              <th className="px-4 py-2.5">Department</th>
              <th className="px-4 py-2.5">Code</th>
              <th className="px-4 py-2.5">Description</th>
              <th className="px-4 py-2.5">Status</th>
              {canWrite && <th className="px-4 py-2.5 w-12" />}
            </tr>
          </thead>
          <tbody>
            {query.isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i}><td colSpan={canWrite ? 5 : 4} className="px-4 py-2.5"><Skeleton className="h-6" /></td></tr>
              ))
            ) : list.length === 0 ? (
              <tr><td colSpan={canWrite ? 5 : 4}><EmptyState title="No departments" icon={<Building2 className="size-5" />} /></td></tr>
            ) : list.map((d, i) => (
              <tr key={String(d.id)} className={`border-t border-border ${i % 2 === 1 ? "bg-background/20" : ""}`}>
                <td className="px-4 py-2.5 font-medium">{d.name}</td>
                <td className="px-4 py-2.5 text-muted-foreground">{d.code ?? "—"}</td>
                <td className="px-4 py-2.5 text-muted-foreground">{d.description ?? "—"}</td>
                <td className="px-4 py-2.5">{d.is_active ? "Active" : "Inactive"}</td>
                {canWrite && (
                  <td className="px-4 py-2.5">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="size-8"><MoreHorizontal className="size-4" /></Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => { setEditDept(d); setFormOpen(true); }}>
                          <Pencil className="size-3.5 mr-2" /> Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem className="text-destructive" onClick={() => void handleDeactivate(d)}>
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

      <DepartmentFormDialog open={formOpen} onOpenChange={setFormOpen} department={editDept} />
    </div>
  );
}
