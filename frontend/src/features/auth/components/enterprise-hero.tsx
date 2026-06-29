import { Boxes, FileBarChart2, Wrench, Sparkles } from "lucide-react";

const ORBIT_ITEMS = [
  { Icon: Boxes, label: "Assets", angle: 0 },
  { Icon: Wrench, label: "Maintenance", angle: 90 },
  { Icon: Sparkles, label: "Analytics", angle: 180 },
  { Icon: FileBarChart2, label: "Reports", angle: 270 },
];

export function EnterpriseHero() {
  return (
    <div className="relative flex items-center justify-center py-8">
      <style>{`
        @keyframes orbit-spin {
          from { transform: rotateY(0deg); }
          to { transform: rotateY(360deg); }
        }
        @keyframes float-card {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-6px); }
        }
        .enterprise-orbit {
          animation: orbit-spin 14s linear infinite;
          transform-style: preserve-3d;
        }
        @media (prefers-reduced-motion: reduce) {
          .enterprise-orbit { animation: none; }
        }
      `}</style>
      <div
        className="relative size-64"
        style={{ perspective: "800px" }}
      >
        <div className="absolute inset-0 grid place-items-center">
          <div className="size-20 rounded-2xl bg-gradient-to-br from-[oklch(0.65_0.22_285)] to-[oklch(0.6_0.2_245)] grid place-items-center text-white text-3xl font-bold shadow-[0_0_40px_rgba(120,100,255,0.45)] z-10">
            A
          </div>
        </div>
        <div className="enterprise-orbit absolute inset-0">
          {ORBIT_ITEMS.map(({ Icon, label, angle }) => (
            <div
              key={label}
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
              style={{
                transform: `rotateY(${angle}deg) translateZ(110px)`,
                transformStyle: "preserve-3d",
              }}
            >
              <div
                className="flex flex-col items-center gap-1.5 p-3 rounded-xl border border-white/10 bg-card/80 backdrop-blur-sm shadow-lg w-24"
                style={{ animation: "float-card 3s ease-in-out infinite", animationDelay: `${angle / 90}s` }}
              >
                <Icon className="size-5 text-[oklch(0.78_0.16_285)]" />
                <span className="text-[10px] text-muted-foreground text-center leading-tight">{label}</span>
              </div>
            </div>
          ))}
        </div>
        <div className="absolute inset-0 rounded-full border border-white/5 pointer-events-none" />
      </div>
    </div>
  );
}
