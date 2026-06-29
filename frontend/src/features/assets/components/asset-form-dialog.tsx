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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DepartmentSelect } from "@/features/departments/components/department-select";
import { useAssetLookups, useCreateAsset, useUpdateAsset } from "@/features/assets/hooks";
import type { Asset } from "@/lib/types/backend";
import { toast } from "@/lib/toast";

type Props = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  asset?: Asset | null;
};

const emptyForm = {
  asset_tag: "",
  name: "",
  asset_type_id: "",
  purchase_date: new Date().toISOString().slice(0, 10),
  purchase_cost: "",
  current_location: "",
  current_department_id: "",
  serial_number: "",
  manufacturer: "",
  model: "",
  warranty_expiry: "",
};

export function AssetFormDialog({ open, onOpenChange, asset }: Props) {
  const isEdit = Boolean(asset);
  const [form, setForm] = useState(emptyForm);
  const { types } = useAssetLookups();
  const create = useCreateAsset();
  const update = useUpdateAsset(asset?.id ?? "");

  useEffect(() => {
    if (!open) return;
    if (asset) {
      setForm({
        asset_tag: asset.asset_tag,
        name: asset.name,
        asset_type_id: asset.asset_type_id,
        purchase_date: asset.purchase_date?.slice(0, 10) ?? "",
        purchase_cost: asset.purchase_cost ?? "",
        current_location: asset.current_location ?? "",
        current_department_id: asset.current_department_id,
        serial_number: asset.serial_number ?? "",
        manufacturer: asset.manufacturer ?? "",
        model: asset.model ?? "",
        warranty_expiry: asset.warranty_expiry?.slice(0, 10) ?? "",
      });
    } else {
      setForm(emptyForm);
    }
  }, [open, asset]);

  const set = (key: keyof typeof form, value: string) => setForm((f) => ({ ...f, [key]: value }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      asset_tag: form.asset_tag.trim(),
      name: form.name.trim(),
      asset_type_id: form.asset_type_id,
      purchase_date: form.purchase_date,
      purchase_cost: parseFloat(form.purchase_cost) || 0,
      current_location: form.current_location.trim() || "Unassigned",
      current_department_id: form.current_department_id,
      serial_number: form.serial_number.trim() || null,
      manufacturer: form.manufacturer.trim() || null,
      model: form.model.trim() || null,
      warranty_expiry: form.warranty_expiry || null,
    };
    try {
      if (isEdit && asset) {
        await update.mutateAsync(payload);
        toast("Asset updated");
      } else {
        await create.mutateAsync(payload);
        toast("Asset registered");
      }
      onOpenChange(false);
    } catch (err) {
      toast((err as Error).message, "error");
    }
  };

  const pending = create.isPending || update.isPending;
  const typeList = types.data ?? [];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEdit ? "Edit asset" : "Register asset"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="asset_tag">Asset tag</Label>
              <Input
                id="asset_tag"
                value={form.asset_tag}
                onChange={(e) => set("asset_tag", e.target.value)}
                required
                className="rounded-lg"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                value={form.name}
                onChange={(e) => set("name", e.target.value)}
                required
                className="rounded-lg"
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label>Type</Label>
            <Select
              value={form.asset_type_id || undefined}
              onValueChange={(v) => set("asset_type_id", v)}
              disabled={types.isLoading}
            >
              <SelectTrigger className="rounded-lg">
                <SelectValue placeholder={types.isLoading ? "Loading types…" : "Select type…"} />
              </SelectTrigger>
              <SelectContent>
                {typeList.map((t) => (
                  <SelectItem key={t.id} value={t.id}>{t.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="purchase_date">Purchase date</Label>
              <Input
                id="purchase_date"
                type="date"
                value={form.purchase_date}
                onChange={(e) => set("purchase_date", e.target.value)}
                required
                className="rounded-lg"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="purchase_cost">Purchase cost</Label>
              <Input
                id="purchase_cost"
                type="number"
                step="0.01"
                min="0"
                value={form.purchase_cost}
                onChange={(e) => set("purchase_cost", e.target.value)}
                required
                className="rounded-lg"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <DepartmentSelect
              value={form.current_department_id}
              onChange={(v) => set("current_department_id", v)}
              required
              enabled={open}
            />
            <div className="space-y-1.5">
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                value={form.current_location}
                onChange={(e) => set("current_location", e.target.value)}
                className="rounded-lg"
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="serial">Serial number</Label>
              <Input id="serial" value={form.serial_number} onChange={(e) => set("serial_number", e.target.value)} className="rounded-lg" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="warranty">Warranty expiry</Label>
              <Input id="warranty" type="date" value={form.warranty_expiry} onChange={(e) => set("warranty_expiry", e.target.value)} className="rounded-lg" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="manufacturer">Manufacturer</Label>
              <Input id="manufacturer" value={form.manufacturer} onChange={(e) => set("manufacturer", e.target.value)} className="rounded-lg" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="model">Model</Label>
              <Input id="model" value={form.model} onChange={(e) => set("model", e.target.value)} className="rounded-lg" />
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
            <Button type="submit" disabled={pending || !form.asset_type_id || !form.current_department_id}>
              {pending ? "Saving…" : isEdit ? "Save changes" : "Register"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
