import { useEffect, useState } from "react";

import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { DepartmentSelect } from "@/features/departments/components/department-select";
import { useCreateEmployee, useUpdateEmployee } from "@/features/employees/hooks";
import type { Employee } from "@/lib/types/backend";
import { toast } from "@/lib/toast";

type Props = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  employee?: Employee | null;
};

export function EmployeeFormDialog({ open, onOpenChange, employee }: Props) {
  const isEdit = Boolean(employee);
  const [departmentId, setDepartmentId] = useState("");
  const [employeeCode, setEmployeeCode] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const create = useCreateEmployee();
  const update = useUpdateEmployee();

  useEffect(() => {
    if (!open) return;
    if (employee) {
      setDepartmentId(employee.department_id);
      setEmployeeCode(employee.employee_code);
      setFirstName(employee.first_name);
      setLastName(employee.last_name);
      setEmail(employee.email);
      setJobTitle(employee.job_title ?? "");
    } else {
      setDepartmentId("");
      setEmployeeCode("");
      setFirstName("");
      setLastName("");
      setEmail("");
      setJobTitle("");
    }
  }, [open, employee]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      department_id: departmentId,
      employee_code: employeeCode.trim(),
      first_name: firstName.trim(),
      last_name: lastName.trim(),
      email: email.trim(),
      job_title: jobTitle.trim() || null,
    };
    try {
      if (isEdit && employee) {
        await update.mutateAsync({ id: employee.id, data: payload });
        toast("Employee updated");
      } else {
        await create.mutateAsync(payload);
        toast("Employee created");
      }
      onOpenChange(false);
    } catch (err) {
      toast((err as Error).message, "error");
    }
  };

  const pending = create.isPending || update.isPending;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit employee" : "Add employee"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <DepartmentSelect
            value={departmentId}
            onChange={setDepartmentId}
            required
            enabled={open}
          />
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>First name</Label>
              <Input value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
            </div>
            <div className="space-y-1.5">
              <Label>Last name</Label>
              <Input value={lastName} onChange={(e) => setLastName(e.target.value)} required />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label>Employee code</Label>
              <Input value={employeeCode} onChange={(e) => setEmployeeCode(e.target.value)} required />
            </div>
            <div className="space-y-1.5">
              <Label>Job title</Label>
              <Input value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label>Email</Label>
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button type="submit" disabled={pending || !departmentId}>{pending ? "Saving…" : "Save"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
