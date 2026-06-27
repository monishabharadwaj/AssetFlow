import {
  BarChart3,
  Building2,
  ClipboardList,
  LayoutGrid,
  Settings,
  Users,
} from "lucide-react";
import { NavLink } from "react-router-dom";

import { cn } from "../../shared/lib/utils";

const navItems = [
  { label: "Operations", to: "/dashboard", icon: LayoutGrid },
  { label: "Assets", to: "/assets", icon: BarChart3 },
  { label: "Maintenance", to: "/maintenance", icon: ClipboardList },
  { label: "Departments", to: "/departments", icon: Building2 },
  { label: "Employees", to: "/employees", icon: Users },
];

export function Sidebar() {
  return (
    <aside className="hidden w-72 border-r border-slate-800 bg-[#111827] md:flex md:flex-col">
      <div className="border-b border-white/10 px-6 py-4">
        <p className="text-xs uppercase tracking-wide text-white/40">
          AssetFlow AI
        </p>
        <h1 className="mt-1 text-lg font-semibold text-white">
          Operations Console
        </h1>
      </div>
      <nav className="space-y-1 px-3 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg border border-transparent px-3 py-2 text-sm transition-all duration-300",
                isActive
                  ? "bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-[0_0_10px_rgba(168,85,247,0.45)]"
                  : "text-white/50 hover:bg-white/5 hover:text-white",
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto border-t border-white/10 px-3 py-3">
        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-white/40 transition-colors hover:bg-white/5 hover:text-white">
          <Settings className="h-4 w-4" />
          Settings
        </button>
      </div>
    </aside>
  );
}
