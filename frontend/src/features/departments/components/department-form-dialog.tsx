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
import { Textarea } from "@/components/ui/textarea";
import { useCreateDepartment, useUpdateDepartment } from "@/features/departments/hooks";
import type { Department } from "@/lib/types/backend";
import { toast } from "@/lib/toast";

type Props = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  department?: Department | null;
};

export function DepartmentFormDialog({ open, onOpenChange, department }: Props) {
  const isEdit = Boolean(department);
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [description, setDescription] = useState("");
  const create = useCreateDepartment();
  const update = useUpdateDepartment();

  useEffect(() => {
    if (!open) return;
    if (department) {
      setName(department.name);
      setCode(department.code);
      setDescription(department.description ?? "");
    } else {
      setName("");
      setCode("");
      setDescription("");
    }
  }, [open, department]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = { name: name.trim(), code: code.trim(), description: description.trim() || null };
    try {
      if (isEdit && department) {
        await update.mutateAsync({ id: department.id, data: payload });
        toast("Department updated");
      } else {
        await create.mutateAsync(payload);
        toast("Department created");
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
          <DialogTitle>{isEdit ? "Edit department" : "Add department"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <div className="space-y-1.5">
            <Label>Name</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label>Code</Label>
            <Input value={code} onChange={(e) => setCode(e.target.value)} required />
          </div>
          <div className="space-y-1.5">
            <Label>Description</Label>
            <Textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button type="submit" disabled={pending}>{pending ? "Saving…" : "Save"}</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
