import AssetsIcon from "../../../assets/icons/Assets.png";
import addassetIcon from "../../../assets/icons/addasset.png";
import maintenanceIcon from "../../../assets/icons/maintenance.png";
import { Link } from "react-router-dom";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../shared/components/ui/card";
import { cn } from "../../../shared/lib/utils";

export function QuickActionsPanel() {
  const linkClass = cn(
    "flex w-full items-center rounded-xl border border-slate-700 bg-slate-900 px-4 py-3 text-slate-200 transition-all duration-300",
    "hover:border-blue-500/30 hover:bg-slate-800 hover:text-white hover:shadow-[0_0_18px_rgba(59,130,246,0.25)]",
  );

  return (
    <Card className="h-full rounded-2xl border border-slate-700 bg-[#111827] shadow-[0_0_25px_rgba(59,130,246,0.08)]">
      <CardHeader>
        <CardTitle className="text-xl font-semibold text-white">
          Quick Actions
        </CardTitle>
        <CardDescription className="text-slate-400">
          Common lifecycle operations
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        <Link to="/assets?create=true" className={linkClass}>
          <img
            src={AssetsIcon}
            alt="Assets"
            className="h-14 w-14 object-contain
             transition-all duration-300
             drop-shadow-[0_0_12px_rgba(6,182,212,0.45)]
             hover:scale-105
             hover:drop-shadow-[0_0_20px_rgba(6,182,212,0.75)]"
          />
          Register Asset
        </Link>
        <Link to="/assets" className={linkClass}>
          <img
            src={addassetIcon}
            alt="Add Assets"
            className="h-14 w-14 object-contain
             transition-all duration-300
             drop-shadow-[0_0_12px_rgba(6,182,212,0.45)]
             hover:scale-105
             hover:drop-shadow-[0_0_20px_rgba(6,182,212,0.75)]"
          />
          Assign Asset
        </Link>
        <Link to="/maintenance" className={linkClass}>
          <img
            src={maintenanceIcon}
            alt="Create Maintenance"
            className="h-14 w-14 object-contain
             transition-all duration-300
             drop-shadow-[0_0_12px_rgba(6,182,212,0.45)]
             hover:scale-105
             hover:drop-shadow-[0_0_20px_rgba(6,182,212,0.75)]"
          />
          Create Maintenance
        </Link>
      </CardContent>
    </Card>
  );
}
