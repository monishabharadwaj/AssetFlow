import { useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";

import { PageHeader } from "../../../shared/components/data-display/page-header";
import { EntityDataTable, type ColumnDef } from "../../../shared/components/data-display/entity-data-table";
import { EntityFiltersBar, FilterField } from "../../../shared/components/data-display/entity-filters-bar";
import { PaginationBar } from "../../../shared/components/data-display/pagination-bar";
import { ConfirmDialog } from "../../../shared/components/feedback/confirm-dialog";
import { FormDialog } from "../../../shared/components/feedback/form-dialog";
import { useToast } from "../../../shared/components/feedback/toast-provider";
import { Button } from "../../../shared/components/ui/button";
import { Input } from "../../../shared/components/ui/input";
import { Label } from "../../../shared/components/ui/label";
import { Textarea } from "../../../shared/components/ui/textarea";
import { useUrlSearchParams } from "../../../shared/hooks/use-url-search-params";
import type { Department, DepartmentCreate } from "../../../shared/api/types";
import { useDepartmentMutations, useDepartmentsList } from "../hooks/use-departments";

const DEFAULT_PARAMS = { page: 1, page_size: 20, search: "" };

export function DepartmentsPageContent() {
  const [params, setParams] = useUrlSearchParams(DEFAULT_PARAMS);
  const { toast } = useToast();
  const { data, isLoading } = useDepartmentsList(params);
  const { create, update, deactivate } = useDepartmentMutations();

  const [formOpen, setFormOpen] = useState(false);
  const [editDept, setEditDept] = useState<Department | null>(null);
  const [deactivateId, setDeactivateId] = useState<string | null>(null);
  const [form, setForm] = useState<DepartmentCreate>({ name: "", code: "", description: "" });

  const openCreate = () => {
    setEditDept(null);
    setForm({ name: "", code: "", description: "" });
    setFormOpen(true);
  };

  const openEdit = (dept: Department) => {
    setEditDept(dept);
    setForm({ name: dept.name, code: dept.code, description: dept.description ?? "" });
    setFormOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editDept) {
        await update.mutateAsync({ id: editDept.id, data: form });
        toast("Department updated");
      } else {
        await create.mutateAsync(form);
        toast("Department created");
      }
      setFormOpen(false);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to save", "error");
    }
  };

  const handleDeactivate = async () => {
    if (!deactivateId) return;
    try {
      await deactivate.mutateAsync(deactivateId);
      toast("Department deactivated");
      setDeactivateId(null);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to deactivate", "error");
    }
  };

  const columns: ColumnDef<Department>[] = [
    { id: "code", header: "Code", cell: (r) => r.code },
    { id: "name", header: "Name", cell: (r) => r.name },
    { id: "desc", header: "Description", cell: (r) => r.description ?? "—" },
    { id: "active", header: "Active", cell: (r) => (r.is_active ? "Yes" : "No") },
    {
      id: "actions",
      header: "",
      cell: (r) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => openEdit(r)}>
            <Pencil className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={() => setDeactivateId(r.id)}>
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="grid gap-4 md:gap-6">
      <PageHeader
        title="Departments"
        description="Manage organizational departments."
        actions={
          <Button type="button" onClick={openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Add Department
          </Button>
        }
      />

      <EntityFiltersBar>
        <FilterField label="Search" className="min-w-[200px] flex-1">
          <Input
            placeholder="Search by name or code"
            value={params.search}
            onChange={(e) => setParams({ search: e.target.value, page: 1 })}
          />
        </FilterField>
      </EntityFiltersBar>

      <EntityDataTable
        columns={columns}
        data={data?.items ?? []}
        isLoading={isLoading}
        rowKey={(r) => r.id}
      />

      {data ? (
        <PaginationBar
          page={data.page}
          pages={data.pages}
          total={data.total}
          pageSize={data.page_size}
          onPageChange={(page) => setParams({ page })}
        />
      ) : null}

      <FormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        title={editDept ? "Edit Department" : "Add Department"}
        onSubmit={handleSubmit}
        isSubmitting={create.isPending || update.isPending}
      >
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Name</Label>
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </div>
          <div className="space-y-2">
            <Label>Code</Label>
            <Input value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} required />
          </div>
          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea
              value={form.description ?? ""}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
        </div>
      </FormDialog>

      <ConfirmDialog
        open={Boolean(deactivateId)}
        onOpenChange={(open) => !open && setDeactivateId(null)}
        title="Deactivate department?"
        description="This will mark the department as inactive."
        confirmLabel="Deactivate"
        destructive
        isConfirming={deactivate.isPending}
        onConfirm={handleDeactivate}
      />
    </div>
  );
}
