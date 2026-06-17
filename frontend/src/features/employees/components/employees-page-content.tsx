import { useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";

import { PageHeader } from "../../../shared/components/data-display/page-header";
import { EntityDataTable, type ColumnDef } from "../../../shared/components/data-display/entity-data-table";
import { EntityFiltersBar, FilterField } from "../../../shared/components/data-display/entity-filters-bar";
import { PaginationBar } from "../../../shared/components/data-display/pagination-bar";
import { ActionSheet } from "../../../shared/components/feedback/action-sheet";
import { ConfirmDialog } from "../../../shared/components/feedback/confirm-dialog";
import { FormDialog } from "../../../shared/components/feedback/form-dialog";
import { useToast } from "../../../shared/components/feedback/toast-provider";
import { Button } from "../../../shared/components/ui/button";
import { Input } from "../../../shared/components/ui/input";
import { Label } from "../../../shared/components/ui/label";
import { Select } from "../../../shared/components/ui/select";
import { formatDate } from "../../../shared/lib/format";
import { useUrlSearchParams } from "../../../shared/hooks/use-url-search-params";
import type { Allocation, Employee, EmployeeCreate } from "../../../shared/api/types";
import { useDepartmentsList } from "../../departments/hooks/use-departments";
import { useEmployeeAllocations, useEmployeeMutations, useEmployeesList } from "../hooks/use-employees";

const DEFAULT_PARAMS = { page: 1, page_size: 20, search: "", department_id: "" };

export function EmployeesPageContent() {
  const [params, setParams] = useUrlSearchParams(DEFAULT_PARAMS);
  const { toast } = useToast();
  const { data, isLoading } = useEmployeesList({
    page: params.page,
    page_size: params.page_size,
    search: params.search || undefined,
    department_id: params.department_id || undefined,
  });
  const { data: deptData } = useDepartmentsList({ page: 1, page_size: 100 });
  const { create, update, deactivate } = useEmployeeMutations();

  const [formOpen, setFormOpen] = useState(false);
  const [editEmp, setEditEmp] = useState<Employee | null>(null);
  const [deactivateId, setDeactivateId] = useState<string | null>(null);
  const [historyId, setHistoryId] = useState<string | null>(null);
  const [form, setForm] = useState<EmployeeCreate>({
    department_id: "",
    employee_code: "",
    first_name: "",
    last_name: "",
    email: "",
    job_title: "",
  });

  const { data: allocData, isLoading: allocLoading } = useEmployeeAllocations(historyId ?? "", 1, 20);

  const openCreate = () => {
    setEditEmp(null);
    setForm({
      department_id: "",
      employee_code: "",
      first_name: "",
      last_name: "",
      email: "",
      job_title: "",
    });
    setFormOpen(true);
  };

  const openEdit = (emp: Employee) => {
    setEditEmp(emp);
    setForm({
      department_id: emp.department_id,
      employee_code: emp.employee_code,
      first_name: emp.first_name,
      last_name: emp.last_name,
      email: emp.email,
      job_title: emp.job_title ?? "",
    });
    setFormOpen(true);
  };

  const handleSubmit = async () => {
    try {
      if (editEmp) {
        await update.mutateAsync({ id: editEmp.id, data: form });
        toast("Employee updated");
      } else {
        await create.mutateAsync(form);
        toast("Employee created");
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
      toast("Employee deactivated");
      setDeactivateId(null);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to deactivate", "error");
    }
  };

  const deptMap = new Map(deptData?.items.map((d) => [d.id, d.name]) ?? []);

  const columns: ColumnDef<Employee>[] = [
    { id: "code", header: "Code", cell: (r) => r.employee_code },
    { id: "name", header: "Name", cell: (r) => `${r.first_name} ${r.last_name}` },
    { id: "email", header: "Email", cell: (r) => r.email },
    { id: "dept", header: "Department", cell: (r) => deptMap.get(r.department_id) ?? "—" },
    { id: "title", header: "Job Title", cell: (r) => r.job_title ?? "—" },
    {
      id: "actions",
      header: "",
      cell: (r) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="sm" onClick={() => setHistoryId(r.id)}>
            History
          </Button>
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

  const allocColumns: ColumnDef<Allocation>[] = [
    { id: "action", header: "Action", cell: (r) => r.action },
    { id: "asset", header: "Asset", cell: (r) => r.asset_id.slice(0, 8) + "…" },
    { id: "allocated", header: "Allocated", cell: (r) => formatDate(r.allocated_at) },
    { id: "returned", header: "Returned", cell: (r) => formatDate(r.returned_at) },
  ];

  return (
    <div className="grid gap-4 md:gap-6">
      <PageHeader
        title="Employees"
        description="Manage employees and view allocation history."
        actions={
          <Button type="button" onClick={openCreate}>
            <Plus className="mr-2 h-4 w-4" />
            Add Employee
          </Button>
        }
      />

      <EntityFiltersBar>
        <FilterField label="Search" className="min-w-[160px] flex-1">
          <Input
            placeholder="Search employees"
            value={params.search}
            onChange={(e) => setParams({ search: e.target.value, page: 1 })}
          />
        </FilterField>
        <FilterField label="Department">
          <Select
            value={params.department_id}
            onChange={(e) => setParams({ department_id: e.target.value, page: 1 })}
          >
            <option value="">All departments</option>
            {deptData?.items.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name}
              </option>
            ))}
          </Select>
        </FilterField>
      </EntityFiltersBar>

      <EntityDataTable columns={columns} data={data?.items ?? []} isLoading={isLoading} rowKey={(r) => r.id} />

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
        title={editEmp ? "Edit Employee" : "Add Employee"}
        onSubmit={handleSubmit}
        isSubmitting={create.isPending || update.isPending}
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2 sm:col-span-2">
            <Label>Department</Label>
            <Select
              value={form.department_id}
              onChange={(e) => setForm({ ...form, department_id: e.target.value })}
            >
              <option value="">Select department</option>
              {deptData?.items.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Employee Code</Label>
            <Input
              value={form.employee_code}
              onChange={(e) => setForm({ ...form, employee_code: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label>Email</Label>
            <Input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label>First Name</Label>
            <Input
              value={form.first_name}
              onChange={(e) => setForm({ ...form, first_name: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label>Last Name</Label>
            <Input
              value={form.last_name}
              onChange={(e) => setForm({ ...form, last_name: e.target.value })}
            />
          </div>
          <div className="space-y-2 sm:col-span-2">
            <Label>Job Title</Label>
            <Input
              value={form.job_title ?? ""}
              onChange={(e) => setForm({ ...form, job_title: e.target.value })}
            />
          </div>
        </div>
      </FormDialog>

      <ConfirmDialog
        open={Boolean(deactivateId)}
        onOpenChange={(open) => !open && setDeactivateId(null)}
        title="Deactivate employee?"
        description="This will mark the employee as inactive."
        confirmLabel="Deactivate"
        destructive
        isConfirming={deactivate.isPending}
        onConfirm={handleDeactivate}
      />

      <ActionSheet
        open={Boolean(historyId)}
        onOpenChange={(open) => !open && setHistoryId(null)}
        title="Allocation History"
        description="Past asset assignments for this employee."
      >
        <EntityDataTable
          columns={allocColumns}
          data={allocData?.items ?? []}
          isLoading={allocLoading}
          rowKey={(r) => r.id}
          emptyMessage="No allocation history."
        />
      </ActionSheet>
    </div>
  );
}
