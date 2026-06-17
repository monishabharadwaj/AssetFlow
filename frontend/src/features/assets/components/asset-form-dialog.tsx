import { useEffect, useState } from "react";

import { Label } from "../../../shared/components/ui/label";
import { Input } from "../../../shared/components/ui/input";
import { Select } from "../../../shared/components/ui/select";
import { FormDialog } from "../../../shared/components/feedback/form-dialog";
import { useToast } from "../../../shared/components/feedback/toast-provider";
import type { Asset, AssetCreate, AssetUpdate } from "../../../shared/api/types";
import { useDepartmentsList } from "../../departments/hooks/use-departments";
import { useAssetMutations, useLookups } from "../hooks/use-assets";

type AssetFormDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  asset?: Asset | null;
};

const emptyCreate: AssetCreate = {
  asset_tag: "",
  name: "",
  asset_type_id: "",
  purchase_date: new Date().toISOString().slice(0, 10),
  purchase_cost: 0,
  current_location: "Unassigned",
  current_department_id: "",
};

export function AssetFormDialog({ open, onOpenChange, asset }: AssetFormDialogProps) {
  const isEdit = Boolean(asset);
  const { toast } = useToast();
  const { create, update } = useAssetMutations();
  const { categories, types } = useLookups();
  const { data: deptData } = useDepartmentsList({ page: 1, page_size: 100, is_active: true });

  const [form, setForm] = useState<AssetCreate>(emptyCreate);
  const [categoryId, setCategoryId] = useState("");

  useEffect(() => {
    if (asset) {
      setForm({
        asset_tag: asset.asset_tag,
        name: asset.name,
        asset_type_id: asset.asset_type_id,
        purchase_date: asset.purchase_date,
        purchase_cost: parseFloat(asset.purchase_cost),
        current_location: asset.current_location,
        current_department_id: asset.current_department_id,
        serial_number: asset.serial_number,
        manufacturer: asset.manufacturer,
        model: asset.model,
        warranty_expiry: asset.warranty_expiry,
      });
      const type = types.data?.find((t) => t.id === asset.asset_type_id);
      if (type) setCategoryId(type.category_id);
    } else {
      setForm(emptyCreate);
      setCategoryId("");
    }
  }, [asset, open, types.data]);

  const filteredTypes = types.data?.filter((t) => !categoryId || t.category_id === categoryId) ?? [];

  const handleSubmit = async () => {
    try {
      if (isEdit && asset) {
        const updateData: AssetUpdate = {
          asset_tag: form.asset_tag,
          name: form.name,
          asset_type_id: form.asset_type_id,
          purchase_date: form.purchase_date,
          purchase_cost: form.purchase_cost,
          current_location: form.current_location,
          current_department_id: form.current_department_id,
          serial_number: form.serial_number,
          manufacturer: form.manufacturer,
          model: form.model,
          warranty_expiry: form.warranty_expiry,
        };
        await update.mutateAsync({ id: asset.id, data: updateData });
        toast("Asset updated successfully");
      } else {
        await create.mutateAsync(form);
        toast("Asset registered successfully");
      }
      onOpenChange(false);
    } catch (err) {
      toast(err instanceof Error ? err.message : "Failed to save asset", "error");
    }
  };

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title={isEdit ? "Edit Asset" : "Register Asset"}
      description={isEdit ? "Update asset metadata." : "Add a new asset to the registry."}
      onSubmit={handleSubmit}
      submitLabel={isEdit ? "Update" : "Register"}
      isSubmitting={create.isPending || update.isPending}
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="asset_tag">Asset Tag</Label>
          <Input
            id="asset_tag"
            value={form.asset_tag}
            onChange={(e) => setForm({ ...form, asset_tag: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="category">Category</Label>
          <Select
            id="category"
            value={categoryId}
            onChange={(e) => {
              setCategoryId(e.target.value);
              setForm({ ...form, asset_type_id: "" });
            }}
          >
            <option value="">Select category</option>
            {categories.data?.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="asset_type">Type</Label>
          <Select
            id="asset_type"
            value={form.asset_type_id}
            onChange={(e) => setForm({ ...form, asset_type_id: e.target.value })}
            required
          >
            <option value="">Select type</option>
            {filteredTypes.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="department">Department</Label>
          <Select
            id="department"
            value={form.current_department_id}
            onChange={(e) => setForm({ ...form, current_department_id: e.target.value })}
            required
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
          <Label htmlFor="location">Location</Label>
          <Input
            id="location"
            value={form.current_location ?? ""}
            onChange={(e) => setForm({ ...form, current_location: e.target.value })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="purchase_date">Purchase Date</Label>
          <Input
            id="purchase_date"
            type="date"
            value={form.purchase_date}
            onChange={(e) => setForm({ ...form, purchase_date: e.target.value })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="purchase_cost">Purchase Cost</Label>
          <Input
            id="purchase_cost"
            type="number"
            min={0}
            step="0.01"
            value={form.purchase_cost}
            onChange={(e) => setForm({ ...form, purchase_cost: parseFloat(e.target.value) || 0 })}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="serial">Serial Number</Label>
          <Input
            id="serial"
            value={form.serial_number ?? ""}
            onChange={(e) => setForm({ ...form, serial_number: e.target.value || null })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="manufacturer">Manufacturer</Label>
          <Input
            id="manufacturer"
            value={form.manufacturer ?? ""}
            onChange={(e) => setForm({ ...form, manufacturer: e.target.value || null })}
          />
        </div>
      </div>
    </FormDialog>
  );
}
