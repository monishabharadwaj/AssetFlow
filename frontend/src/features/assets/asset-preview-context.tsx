import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

import { AssetPreviewDialog } from "@/features/assets/components/asset-preview-dialog";

export type AssetPreviewData = {
  assetId: string;
  assetTag: string;
  assetName: string;
  assetTypeName?: string | null;
  healthScore?: number | null;
  riskLevel?: string | null;
};

type AssetPreviewContextValue = {
  openPreview: (data: AssetPreviewData) => void;
  closePreview: () => void;
};

const AssetPreviewContext = createContext<AssetPreviewContextValue | null>(null);

export function AssetPreviewProvider({ children }: { children: ReactNode }) {
  const [preview, setPreview] = useState<AssetPreviewData | null>(null);

  const openPreview = useCallback((data: AssetPreviewData) => setPreview(data), []);
  const closePreview = useCallback(() => setPreview(null), []);

  const value = useMemo(() => ({ openPreview, closePreview }), [openPreview, closePreview]);

  return (
    <AssetPreviewContext.Provider value={value}>
      {children}
      <AssetPreviewDialog data={preview} onClose={closePreview} />
    </AssetPreviewContext.Provider>
  );
}

export function useAssetPreview() {
  const ctx = useContext(AssetPreviewContext);
  if (!ctx) throw new Error("useAssetPreview must be used within AssetPreviewProvider");
  return ctx;
}

export function useAssetPreviewOptional() {
  return useContext(AssetPreviewContext);
}
