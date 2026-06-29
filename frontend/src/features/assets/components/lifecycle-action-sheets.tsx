import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea";
import {
  useAssignAsset,
  useCreateMaintenance,
  useReturnAsset,
  useTransferAsset,
} from "@/features/assets/hooks";
import { DepartmentSelect } from "@/features/departments/components/department-select";
import { useEmployees } from "@/features/employees/hooks";
import { MAX_PAGE_SIZE } from "@/lib/constants";
import type { Asset, MaintenanceType } from "@/lib/types/backend";
import { toast } from "@/lib/toast";

type SheetKind = "assign" | "return" | "transfer" | "maintenance" | null;

type Props = {
  asset: Asset;
  kind: SheetKind;
  onClose: () => void;
};

export function LifecycleActionSheet({ asset, kind, onClose }: Props) {
  if (!kind) return null;
  return (
    <Sheet open onOpenChange={(o) => !o && onClose()}>
      <SheetContent className="overflow-y-auto">
        <SheetHeader>
          <SheetTitle>
            {kind === "assign" && "Assign asset"}
            {kind === "return" && "Return asset"}
            {kind === "transfer" && "Transfer asset"}
            {kind === "maintenance" && "Schedule maintenance"}
          </SheetTitle>
        </SheetHeader>
        <div className="mt-6">
          {kind === "assign" && <AssignForm asset={asset} onDone={onClose} />}
          {kind === "return" && <ReturnForm asset={asset} onDone={onClose} />}
          {kind === "transfer" && <TransferForm asset={asset} onDone={onClose} />}
          {kind === "maintenance" && <MaintenanceForm asset={asset} onDone={onClose} />}
        </div>
      </SheetContent>
    </Sheet>
  );
}

function AssignForm({ asset, onDone }: { asset: Asset; onDone: () => void }) {
  const [employeeId, setEmployeeId] = useState("");
  const [notes, setNotes] = useState("");
  const employees = useEmployees({ page: 1, page_size: MAX_PAGE_SIZE, department_id: asset.current_department_id });
  const assign = useAssignAsset(asset.id);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await assign.mutateAsync({
        employee_id: employeeId,
        allocated_at: new Date().toISOString(),
        notes: notes || null,
      });
      toast("Asset assigned");
      onDone();
    } catch (err) {
      toast((err as Error).message, "error");
    }
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="space-y-1.5">
        <Label>Employee</Label>
        <select
          value={employeeId}
          onChange={(e) => setEmployeeId(e.target.value)}
          required
          className="w-full h-9 px-3 rounded-md border border-border bg-background text-sm"
        >
          <option value="">Select employee…</option>
          {(employees.data?.items ?? []).map((emp) => (
            <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name}</option>
          ))}
        </select>
      </div>
      <div className="space-y-1.5">
        <Label>Notes</Label>
        <Textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} />
      </div>
      <Button type="submit" disabled={assign.isPending} className="w-full">
        {assign.isPending ? "Assigning…" : "Assign"}
      </Button>
    </form>
  );
}

function ReturnForm({ asset, onDone }: { asset: Asset; onDone: () => void }) {
  const [notes, setNotes] = useState("");
  const ret = useReturnAsset(asset.id);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await ret.mutateAsync({ returned_at: new Date().toISOString(), notes: notes || null });
      toast("Asset returned");
      onDone();
    } catch (err) {
      toast((err as Error).message, "error");
    }
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      <p className="text-sm text-muted-foreground">Mark this asset as returned from its current assignment.</p>
      <div className="space-y-1.5">
        <Label>Notes</Label>
        <Textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} />
      </div>
      <Button type="submit" disabled={ret.isPending} className="w-full">
        {ret.isPending ? "Processing…" : "Confirm return"}
      </Button>
    </form>
  );
}

function TransferForm({ asset, onDone }: { asset: Asset; onDone: () => void }) {
  const [departmentId, setDepartmentId] = useState(asset.current_department_id);
  const [location, setLocation] = useState(asset.current_location);
  const [notes, setNotes] = useState("");
  const transfer = useTransferAsset(asset.id);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await transfer.mutateAsync({
        to_department_id: departmentId,
        to_location: location,
        transferred_at: new Date().toISOString(),
        reason: notes || null,
      });
      toast("Asset transferred");
      onDone();
    } catch (err) {
      toast((err as Error).message, "error");
    }
  };

  return (
    <form onSubmit={submit} className="space-y-4">
      <DepartmentSelect value={departmentId} onChange={setDepartmentId} required />
      <div className="space-y-1.5">
        <Label>Location</Label>
        <Input value={location} onChange={(e) => setLocation(e.target.value)} required />
      </div>
      <div className="space-y-1.5">
        <Label>Notes</Label>
        <Textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} />
      </div>
      <Button type="submit" disabled={transfer.isPending} className="w-full">
        {transfer.isPending ? "Transferring…" : "Transfer"}
      </Button>
    </form>
  );
}

function MaintenanceForm({ asset, onDone }: { asset: Asset; onDone: () => void }) {
  const [maintenanceType, setMaintenanceType] = useState<MaintenanceType>("PREVENTIVE");
  const [scheduledDate, setScheduledDate] = useState(new Date().toISOString().slice(0, 10));
  const [description, setDescription] = useState("");
  const [provider, setProvider] = useState("");
  const create = useCreateMaintenance(asset.id);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await create.mutateAsync({
        maintenance_type: maintenanceType,
        status: "SCHEDULED",
        scheduled_date: scheduledDate,
        description: description.trim(),
        service_provider: provider.trim() || null,
      });
      toast("Maintenance scheduled");
      onDone();
    } catch (err) {
      toast((err as Error).message, "error");
    }
  };

  const types: MaintenanceType[] = ["PREVENTIVE", "CORRECTIVE", "INSPECTION", "UPGRADE", "OTHER"];

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="space-y-1.5">
        <Label>Type</Label>
        <select
          value={maintenanceType}
          onChange={(e) => setMaintenanceType(e.target.value as MaintenanceType)}
          className="w-full h-9 px-3 rounded-md border border-border bg-background text-sm"
        >
          {types.map((t) => <option key={t} value={t}>{t.replace(/_/g, " ")}</option>)}
        </select>
      </div>
      <div className="space-y-1.5">
        <Label>Scheduled date</Label>
        <Input type="date" value={scheduledDate} onChange={(e) => setScheduledDate(e.target.value)} required />
      </div>
      <div className="space-y-1.5">
        <Label>Description</Label>
        <Textarea value={description} onChange={(e) => setDescription(e.target.value)} required rows={3} />
      </div>
      <div className="space-y-1.5">
        <Label>Service provider</Label>
        <Input value={provider} onChange={(e) => setProvider(e.target.value)} />
      </div>
      <Button type="submit" disabled={create.isPending} className="w-full">
        {create.isPending ? "Scheduling…" : "Schedule"}
      </Button>
    </form>
  );
}
