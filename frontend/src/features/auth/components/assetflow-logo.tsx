import { cn } from "@/lib/utils";

type AssetFlowLogoProps = {
  className?: string;
  size?: "xs" | "sm" | "md" | "lg";
};

const sizes = {
  xs: "size-8",
  sm: "size-9",
  md: "size-14",
  lg: "size-24",
};

const iconSizes = {
  xs: "size-[18px]",
  sm: "size-5",
  md: "size-8",
  lg: "size-14",
};

/** Premium mark: gem hub + orbital flow (asset lifecycle), not a letter monogram. */
export function AssetFlowLogo({ className, size = "sm" }: AssetFlowLogoProps) {
  return (
    <div
      className={cn(
        sizes[size],
        "rounded-xl bg-gradient-to-br from-[oklch(0.68_0.24_285)] via-[oklch(0.62_0.22_275)] to-[oklch(0.55_0.2_245)]",
        "ring-1 ring-inset ring-white/20 shadow-lg glow-primary shrink-0 grid place-items-center",
        className,
      )}
      aria-hidden
    >
      <svg
        viewBox="0 0 32 32"
        fill="none"
        className={iconSizes[size]}
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="af-gem" x1="10" y1="8" x2="22" y2="24" gradientUnits="userSpaceOnUse">
            <stop stopColor="white" stopOpacity="1" />
            <stop offset="1" stopColor="white" stopOpacity="0.82" />
          </linearGradient>
          <linearGradient id="af-orbit" x1="4" y1="16" x2="28" y2="16" gradientUnits="userSpaceOnUse">
            <stop stopColor="white" stopOpacity="0.15" />
            <stop offset="0.5" stopColor="white" stopOpacity="0.55" />
            <stop offset="1" stopColor="white" stopOpacity="0.15" />
          </linearGradient>
        </defs>
        <ellipse
          cx="16"
          cy="16"
          rx="12"
          ry="5"
          stroke="url(#af-orbit)"
          strokeWidth="1.2"
          transform="rotate(-24 16 16)"
        />
        <ellipse
          cx="16"
          cy="16"
          rx="12"
          ry="5"
          stroke="url(#af-orbit)"
          strokeWidth="1.2"
          transform="rotate(28 16 16)"
        />
        <path
          d="M16 8.5 L21.8 16 L16 23.5 L10.2 16 Z"
          fill="url(#af-gem)"
        />
        <path
          d="M16 11.2 L19.2 16 L16 20.8 L12.8 16 Z"
          fill="white"
          fillOpacity="0.22"
        />
        <circle cx="26" cy="10" r="1.6" fill="white" fillOpacity="0.9" />
        <circle cx="7" cy="22" r="1.35" fill="white" fillOpacity="0.75" />
        <path
          d="M20.5 13.5 L25 10.5 M11.5 18.5 L7 21.5"
          stroke="white"
          strokeOpacity="0.45"
          strokeWidth="0.9"
          strokeLinecap="round"
        />
      </svg>
    </div>
  );
}
