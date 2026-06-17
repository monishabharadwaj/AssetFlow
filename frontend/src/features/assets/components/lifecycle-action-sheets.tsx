import { useState } from "react";

import { ActionSheet } from "../../../shared/components/feedback/action-sheet";
import { useToast } from "../../../shared/components/feedback/toast-provider";
import { Button } from "../../../shared/components/ui/button";
import { Input } from "../../../shared/components/ui/input";
import { Label } from "../../../shared/components/ui/label";
import { Select } from "../../../shared/components/ui/select";
import { Textarea } from "../../../shared/components/ui/textarea";
import type { Asset } from "../../../shared/api/types";
import { useDepartmentsList } from "../../departments/hooks/use-departments";
import { useEmployeesList } from "../../employees/hooks/use-employees";
import { useLifecycleMutations } from "../hooks/use-lifecycle";

type LifecycleActionSheetsProps = {
  asset: Asset;
  assignOpen: boolean;
  transferOpen: boolean;
  maintenanceOpen: boolean;
  healthOpen: boolean;
  onAssignOpenChange: (open: boolean) => void;
  onTransferOpenChange: (open: boolean) => void;
  onMaintenanceOpenChange: (open: boolean) => void;
  onHealthOpenChange: (open: boolean) => void;
};

export function LifecycleActionSheets({
  asset,
  assignOpen,
  transferOpen,
  maintenanceOpen,
  healthOpen,
  onAssignOpenChange,
  onTransferOpenChange,
  onMaintenanceOpenChange,
  onHealthOpenChange,
}: LifecycleActionSheetsProps) {
  const { toast } = useToast();
  const mutations = useLifecycleMutations(asset.id);
  const { data: deptData } = useDepartmentsList({ page: 1, page_size: 100, is_active: true });
  const { data: empData } = useEmployeesList({ page: 1, page_size: 100, is_active: true });

  const [employeeId, setEmployeeId] = useState("");
  const [notes, setNotes] = useState("");
  const [toDeptId, setToDeptId] = useState("");
  const [toLocation, setToLocation] = useState("");
  const [transferReason, setTransferReason] = useState("");
  const [maintType, setMaintType] = useState("PREVENTIVE");
  const [maintDesc, setMaintDesc] = useState("");
  const [healthScore, setHealthScore] = useState("");
  const [conditionRating, setConditionRating] = useState("");

  const now = () => new Date().toISOString();

  const handleAssign = async () => {
    try {
      if (asset.current_status === "ASSIGNED") {
        await mutations.reassign.mutateAsync({
          employee_id: employeeId,
          allocated_at: now(),
          notes: notes || null,
        });
        toast("Asset reassigned");
      } else if (asset.current_status === "AVAILABLE") {
        await mutations.assign.mutateAsync({
          employee_id: employeeId,
          allocated_at: now(),
          notes: notes || null,
        });
        toast("Asset assigned");
      }
      onAssignOpenChange(false);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Assignment failed", "error");
    }
  };

  const handleReturn = async () => {
    try {
      await mutations.return.mutateAsync({ returned_at: now(), notes: notes || null });
      toast("Asset returned");
      onAssignOpenChange(false);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Return failed", "error");
    }
  };

  const handleTransfer = async () => {
    try {
      await mutations.transfer.mutateAsync({
        to_department_id: toDeptId,
        to_location: toLocation,
        transferred_at: now(),
        reason: transferReason || null,
      });
      toast("Asset transferred");
      onTransferOpenChange(false);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Transfer failed", "error");
    }
  };

  const handleMaintenance = async () => {
    try {
      await mutations.createMaintenance.mutateAsync({
        maintenance_type: maintType as "PREVENTIVE",
        description: maintDesc,
        status: "SCHEDULED",
      });
      toast("Maintenance record created");
      onMaintenanceOpenChange(false);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to create maintenance", "error");
    }
  };

  const handleHealth = async () => {
    try {
      await mutations.createHealth.mutateAsync({
        health_score: healthScore ? parseFloat(healthScore) : null,
        condition_rating: conditionRating ? parseInt(conditionRating, 10) : null,
      });
      toast("Health snapshot recorded");
      onHealthOpenChange(false);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to record health", "error");
    }
  };

  return (
    <>
      <ActionSheet
        open={assignOpen}
        onOpenChange={onAssignOpenChange}
        title={asset.current_status === "ASSIGNED" ? "Reassign Asset" : "Assign Asset"}
        description="Select an employee for this asset."
      >
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Employee</Label>
            <Select value={employeeId} onChange={(e) => setEmployeeId(e.target.value)}>
              <option value="">Select employee</option>
              {empData?.items.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.first_name} {e.last_name} ({e.employee_code})
                </option>
              ))}
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Notes</Label>
            <Textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
          </div>
          <div className="flex flex-col gap-2">
            <Button type="button" onClick={handleAssign} disabled={!employeeId}>
              {asset.current_status === "ASSIGNED" ? "Reassign" : "Assign"}
            </Button>
            {asset.current_status === "ASSIGNED" ? (
              <Button type="button" variant="secondary" onClick={handleReturn}>
                Return Asset
              </Button>
            ) : null}
          </div>
        </div>
      </ActionSheet>

      <ActionSheet
        open={transferOpen}
        onOpenChange={onTransferOpenChange}
        title="Transfer Asset"
        description="Move asset to a new department and location."
      >
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>To Department</Label>
            <Select value={toDeptId} onChange={(e) => setToDeptId(e.target.value)}>
              <option value="">Select department</option>
              {deptData?.items.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </Select>
          </div>
          <div className="space-y-2">
            <Label>To Location</Label>
            <Input value={toLocation} onChange={(e) => setToLocation(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Reason</Label>
            <Textarea value={transferReason} onChange={(e) => setTransferReason(e.target.value)} />
          </div>
          <Button type="button" onClick={handleTransfer} disabled={!toDeptId || !toLocation}>
            Transfer
          </Button>
        </div>
      </ActionSheet>

      <ActionSheet
        open={maintenanceOpen}
        onOpenChange={onMaintenanceOpenChange}
        title="Add Maintenance"
        description="Create a maintenance record for this asset."
      >
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Type</Label>
            <Select value={maintType} onChange={(e) => setMaintType(e.target.value)}>
              <option value="PREVENTIVE">Preventive</option>
              <option value="CORRECTIVE">Corrective</option>
              <option value="INSPECTION">Inspection</option>
              <option value="UPGRADE">Upgrade</option>
              <option value="OTHER">Other</option>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea value={maintDesc} onChange={(e) => setMaintDesc(e.target.value)} required />
          </div>
          <Button type="button" onClick={handleMaintenance} disabled={!maintDesc}>
            Create Record
          </Button>
        </div>
      </ActionSheet>

      <ActionSheet
        open={healthOpen}
        onOpenChange={onHealthOpenChange}
        title="Health Snapshot"
        description="Record a health assessment for this asset."
      >
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Health Score (0–1)</Label>
            <Input
              type="number"
              min={0}
              max={1}
              step="0.01"
              value={healthScore}
              onChange={(e) => setHealthScore(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label>Condition Rating (1–10)</Label>
            <Input
              type="number"
              min={1}
              max={10}
              value={conditionRating}
              onChange={(e) => setConditionRating(e.target.value)}
            />
          </div>
          <Button type="button" onClick={handleHealth}>
            Record Snapshot
          </Button>
        </div>
      </ActionSheet>
    </>
  );
}
