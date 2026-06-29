import { useState } from "react";
import { Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { EmptyState, Skeleton } from "@/components/ui-bits";
import { useAssetsSearch, useCreateMaintenance } from "@/features/assets/hooks";
import { usePermissions } from "@/features/auth/use-permissions";
import { toast } from "@/lib/toast";
import type { Asset, MaintenanceType } from "@/lib/types/backend";

const MAINTENANCE_TYPES: MaintenanceType[] = ["PREVENTIVE", "CORRECTIVE", "INSPECTION", "UPGRADE", "OTHER"];

export function ScheduleMaintenanceSheet() {
  const { can } = usePermissions();
  const [open, setOpen] = useState(false);
  const [step, setStep] = useState<1 | 2>(1);
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState<Asset | null>(null);

  const search = useAssetsSearch({ q: q.trim() || undefined, page: 1, page_size: 20 }, open && step === 1);

  if (!can("maintenance:write")) return null;

  const reset = () => {
    setStep(1);
    setQ("");
    setSelected(null);
  };

  const close = () => {
    setOpen(false);
    reset();
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="h-9 px-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 text-sm"
      >
        Schedule maintenance
      </button>

      <Sheet open={open} onOpenChange={(v) => (v ? setOpen(true) : close())}>
        <SheetContent className="w-full sm:max-w-md overflow-y-auto">
          <SheetHeader>
            <SheetTitle>Schedule maintenance</SheetTitle>
            <SheetDescription>
              {step === 1 ? "Choose an asset to schedule work for." : `Scheduling for ${selected?.asset_tag}`}
            </SheetDescription>
          </SheetHeader>

          {step === 1 ? (
            <div className="mt-6 space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                <Input
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  placeholder="Search by name or tag…"
                  className="pl-9"
                />
              </div>
              <div className="space-y-2 max-h-[50vh] overflow-y-auto">
                {search.isLoading ? (
                  <><Skeleton className="h-12" /><Skeleton className="h-12" /></>
                ) : (search.data?.items ?? []).length === 0 ? (
                  <EmptyState title="No assets found" hint="Try a different search term." />
                ) : (
                  search.data!.items.map((asset) => (
                    <button
                      key={asset.id}
                      type="button"
                      onClick={() => { setSelected(asset); setStep(2); }}
                      className="w-full text-left rounded-lg border border-border p-3 hover:bg-accent/30 transition-colors"
                    >
                      <div className="font-mono text-xs text-muted-foreground">{asset.asset_tag}</div>
                      <div className="text-sm font-medium mt-0.5">{asset.name}</div>
                    </button>
                  ))
                )}
              </div>
            </div>
          ) : selected ? (
            <ScheduleMaintenanceForm asset={selected} onBack={() => setStep(1)} onDone={close} />
          ) : null}
        </SheetContent>
      </Sheet>
    </>
  );
}

function ScheduleMaintenanceForm({
  asset,
  onBack,
  onDone,
}: {
  asset: Asset;
  onBack: () => void;
  onDone: () => void;
}) {
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

  return (
    <form onSubmit={submit} className="mt-6 space-y-4">
      <button
        type="button"
        onClick={onBack}
        className="text-xs text-muted-foreground hover:text-foreground"
      >
        ← Change asset
      </button>
      <div className="space-y-1.5">
        <Label>Type</Label>
        <select
          value={maintenanceType}
          onChange={(e) => setMaintenanceType(e.target.value as MaintenanceType)}
          className="w-full h-9 px-3 rounded-md border border-border bg-background text-sm"
        >
          {MAINTENANCE_TYPES.map((t) => (
            <option key={t} value={t}>{t.replace(/_/g, " ")}</option>
          ))}
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
