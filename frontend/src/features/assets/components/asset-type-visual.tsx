import { Laptop, Monitor, Printer, Server, HardDrive } from "lucide-react";

import { cn } from "@/lib/utils";

export type AssetVisualVariant = "laptop" | "server_rack" | "printer" | "monitor" | "generic";

export function resolveAssetVisualVariant(typeName?: string | null, assetName?: string | null): AssetVisualVariant {
  const hay = `${typeName ?? ""} ${assetName ?? ""}`.toLowerCase();
  if (hay.includes("server") || hay.includes("rack")) return "server_rack";
  if (hay.includes("laptop") || hay.includes("notebook")) return "laptop";
  if (hay.includes("printer")) return "printer";
  if (hay.includes("monitor") || hay.includes("display")) return "monitor";
  return "generic";
}

const VARIANT_META: Record<AssetVisualVariant, { Icon: typeof Laptop; label: string; shell: string; screen: string }> = {
  laptop: {
    Icon: Laptop,
    label: "Laptop",
    shell: "from-slate-600 to-slate-800",
    screen: "from-sky-400/40 to-indigo-500/30",
  },
  server_rack: {
    Icon: Server,
    label: "Server rack",
    shell: "from-zinc-400 to-zinc-600",
    screen: "from-emerald-400/30 to-cyan-500/20",
  },
  printer: {
    Icon: Printer,
    label: "Printer",
    shell: "from-stone-500 to-stone-700",
    screen: "from-amber-400/30 to-orange-500/20",
  },
  monitor: {
    Icon: Monitor,
    label: "Monitor",
    shell: "from-slate-500 to-slate-700",
    screen: "from-violet-400/30 to-purple-500/20",
  },
  generic: {
    Icon: HardDrive,
    label: "Asset",
    shell: "from-slate-500 to-slate-700",
    screen: "from-[oklch(0.65_0.22_285)]/30 to-[oklch(0.6_0.2_245)]/20",
  },
};

export function AssetTypeVisual({
  typeName,
  assetName,
  size = "md",
  className,
}: {
  typeName?: string | null;
  assetName?: string | null;
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  const variant = resolveAssetVisualVariant(typeName, assetName);
  const meta = VARIANT_META[variant];
  const { Icon } = meta;

  const boxSize = size === "lg" ? "size-40" : size === "sm" ? "size-24" : "size-32";

  return (
    <div className={cn("flex flex-col items-center gap-2", className)}>
      <style>{`
        @keyframes asset-spin3d {
          from { transform: rotateY(0deg); }
          to { transform: rotateY(360deg); }
        }
        .asset-spin3d {
          animation: asset-spin3d 10s linear infinite;
          transform-style: preserve-3d;
        }
        @media (prefers-reduced-motion: reduce) {
          .asset-spin3d { animation: none; }
        }
      `}</style>
      <div style={{ perspective: "600px" }} className={cn(boxSize, "relative")}>
        <div className="asset-spin3d w-full h-full">
          <div
            className={cn(
              "w-full h-full rounded-xl border border-white/15 shadow-xl grid place-items-center bg-gradient-to-br",
              meta.shell,
            )}
          >
            <div
              className={cn(
                "w-[70%] h-[55%] rounded-md border border-white/10 bg-gradient-to-br grid place-items-center",
                meta.screen,
              )}
            >
              <Icon className={cn(size === "lg" ? "size-10" : size === "sm" ? "size-6" : "size-8", "text-white/80")} />
            </div>
          </div>
        </div>
      </div>
      <span className="text-xs text-muted-foreground">{meta.label}</span>
    </div>
  );
}
