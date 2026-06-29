import { Link } from "@tanstack/react-router";

import { AssetTypeVisual } from "@/features/assets/components/asset-type-visual";
import type { AssetPreviewData } from "@/features/assets/asset-preview-context";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Pill } from "@/components/ui-bits";
import { pct } from "@/lib/format";

export function AssetPreviewDialog({
  data,
  onClose,
}: {
  data: AssetPreviewData | null;
  onClose: () => void;
}) {
  return (
    <Dialog open={!!data} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        {data && (
          <>
            <DialogHeader>
              <DialogTitle className="font-mono text-base">{data.assetTag}</DialogTitle>
              <p className="text-sm text-muted-foreground">{data.assetName}</p>
            </DialogHeader>
            <div className="flex flex-col items-center py-4 gap-3">
              <AssetTypeVisual
                typeName={data.assetTypeName}
                assetName={data.assetName}
                size="lg"
              />
              <div className="flex items-center gap-2 flex-wrap justify-center">
                {data.healthScore != null && (
                  <Pill>Health {pct(data.healthScore)}</Pill>
                )}
                {data.riskLevel && (
                  <Pill className={data.riskLevel === "HIGH" ? "bg-critical/15 text-[oklch(0.78_0.22_18)] border-critical/30" : undefined}>
                    {data.riskLevel} risk
                  </Pill>
                )}
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={onClose}>Close</Button>
              <Button asChild>
                <Link
                  to="/assets/$id"
                  params={{ id: data.assetId }}
                  search={{ tab: "intelligence" }}
                  onClick={onClose}
                >
                  View asset details
                </Link>
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
