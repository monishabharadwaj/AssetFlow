import {
  Boxes,
  FileBarChart2,
  Laptop,
  Printer,
  Server,
  Sparkles,
  Truck,
  Wrench,
} from "lucide-react";

import { AssetFlowLogo } from "@/features/auth/components/assetflow-logo";

const INNER_ORBIT = [
  { Icon: Boxes, label: "Assets", angle: 0 },
  { Icon: Wrench, label: "Maintenance", angle: 90 },
  { Icon: Sparkles, label: "Intelligence", angle: 180 },
  { Icon: FileBarChart2, label: "Reports", angle: 270 },
];

const OUTER_ORBIT = [
  { Icon: Laptop, angle: 45 },
  { Icon: Server, angle: 135 },
  { Icon: Printer, angle: 225 },
  { Icon: Truck, angle: 315 },
];

export function EnterpriseHero() {
  return (
    <div className="relative flex items-center justify-center py-4 min-h-[28rem]">
      <style>{`
        @keyframes orbit-inner {
          from { transform: rotateY(0deg); }
          to { transform: rotateY(360deg); }
        }
        @keyframes orbit-outer {
          from { transform: rotateY(360deg); }
          to { transform: rotateY(0deg); }
        }
        @keyframes float-card {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
        @keyframes glow-pulse {
          0%, 100% { box-shadow: 0 0 40px rgba(120, 100, 255, 0.35); transform: scale(1); }
          50% { box-shadow: 0 0 64px rgba(120, 100, 255, 0.55); transform: scale(1.04); }
        }
        .enterprise-orbit-inner {
          animation: orbit-inner 16s linear infinite;
          transform-style: preserve-3d;
        }
        .enterprise-orbit-outer {
          animation: orbit-outer 22s linear infinite;
          transform-style: preserve-3d;
        }
        .enterprise-glow {
          animation: glow-pulse 4s ease-in-out infinite;
        }
        @media (prefers-reduced-motion: reduce) {
          .enterprise-orbit-inner,
          .enterprise-orbit-outer,
          .enterprise-glow { animation: none; }
        }
      `}</style>
      <div className="relative size-[26rem] max-w-full" style={{ perspective: "1000px" }}>
        <div className="absolute inset-6 rounded-full border border-dashed border-white/8 pointer-events-none" />
        <div
          className="absolute inset-0 rounded-full border border-white/5 pointer-events-none"
          style={{ transform: "rotateX(12deg)" }}
        />

        <div className="absolute inset-0 grid place-items-center z-10">
          <div className="enterprise-glow rounded-2xl">
            <AssetFlowLogo size="lg" className="rounded-2xl" />
          </div>
        </div>

        <div className="enterprise-orbit-outer absolute inset-0">
          {OUTER_ORBIT.map(({ Icon, angle }) => (
            <div
              key={angle}
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
              style={{
                transform: `rotateY(${angle}deg) translateZ(175px)`,
                transformStyle: "preserve-3d",
              }}
            >
              <div className="size-11 rounded-lg border border-white/10 bg-card/60 backdrop-blur-sm grid place-items-center shadow-md">
                <Icon className="size-5 text-[oklch(0.72_0.14_285)]/80" />
              </div>
            </div>
          ))}
        </div>

        <div className="enterprise-orbit-inner absolute inset-0">
          {INNER_ORBIT.map(({ Icon, label, angle }) => (
            <div
              key={label}
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
              style={{
                transform: `rotateY(${angle}deg) translateZ(128px)`,
                transformStyle: "preserve-3d",
              }}
            >
              <div
                className="flex flex-col items-center gap-1.5 p-3 rounded-xl border border-white/12 bg-card/85 backdrop-blur-sm shadow-lg w-[6.5rem]"
                style={{
                  animation: "float-card 3.5s ease-in-out infinite",
                  animationDelay: `${angle / 90}s`,
                }}
              >
                <Icon className="size-5 text-[oklch(0.78_0.16_285)]" />
                <span className="text-[10px] text-muted-foreground text-center leading-tight">{label}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
