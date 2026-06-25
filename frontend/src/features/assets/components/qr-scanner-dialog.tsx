import { useCallback, useEffect, useRef, useState } from "react";
import { Html5Qrcode } from "html5-qrcode";
import { useNavigate } from "react-router-dom";

import { searchAssets } from "../api/assets-api";
import { Button } from "../../../shared/components/ui/button";
import { Dialog } from "../../../shared/components/ui/dialog";
import { Input } from "../../../shared/components/ui/input";
import { Label } from "../../../shared/components/ui/label";

type QrScannerDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

const SCANNER_ELEMENT_ID = "assetflow-qr-scanner";

export function QrScannerDialog({ open, onOpenChange }: QrScannerDialogProps) {
  const navigate = useNavigate();
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const [manualTag, setManualTag] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLookingUp, setIsLookingUp] = useState(false);

  const lookupTag = useCallback(
    async (tag: string) => {
      const trimmed = tag.trim();
      if (!trimmed) return;

      setIsLookingUp(true);
      setError(null);
      try {
        const result = await searchAssets({ asset_tag: trimmed, page: 1, page_size: 5 });
        const asset =
          result.items.find((a) => a.asset_tag.toLowerCase() === trimmed.toLowerCase()) ??
          result.items[0];
        if (!asset) {
          setError(`No asset found for tag "${trimmed}".`);
          return;
        }
        onOpenChange(false);
        navigate(`/assets/${asset.id}?tab=timeline`);
      } catch {
        setError("Lookup failed. Check the tag and try again.");
      } finally {
        setIsLookingUp(false);
      }
    },
    [navigate, onOpenChange],
  );

  useEffect(() => {
    if (!open) {
      void scannerRef.current?.stop().catch(() => undefined);
      scannerRef.current = null;
      setError(null);
      return;
    }

    const scanner = new Html5Qrcode(SCANNER_ELEMENT_ID);
    scannerRef.current = scanner;

    scanner
      .start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 220, height: 220 } },
        (decoded) => {
          void lookupTag(decoded);
        },
        () => undefined,
      )
      .catch(() => {
        setError("Camera unavailable. Enter the asset tag manually below.");
      });

    return () => {
      void scanner.stop().catch(() => undefined);
      scannerRef.current = null;
    };
  }, [open, lookupTag]);

  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
      title="Scan Asset QR"
      description="Scan a QR code or enter an asset tag (e.g. IT-LAP-0001) to open the asset story."
      className="sm:max-w-md"
    >
      <div id={SCANNER_ELEMENT_ID} className="min-h-[220px] overflow-hidden rounded-lg border bg-muted/30" />

      <form
        className="mt-4 space-y-2"
        onSubmit={(e) => {
          e.preventDefault();
          void lookupTag(manualTag);
        }}
      >
        <Label htmlFor="manual-tag">Asset tag</Label>
        <div className="flex gap-2">
          <Input
            id="manual-tag"
            placeholder="IT-LAP-0001"
            value={manualTag}
            onChange={(e) => setManualTag(e.target.value)}
          />
          <Button type="submit" disabled={isLookingUp || !manualTag.trim()}>
            Go
          </Button>
        </div>
      </form>

      {error ? <p className="mt-2 text-sm text-destructive">{error}</p> : null}
    </Dialog>
  );
}
