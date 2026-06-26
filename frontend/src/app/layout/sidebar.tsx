import { BarChart3, Building2, ClipboardList, LayoutGrid, Settings, Users } from "lucide-react";
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
    <aside className="hidden w-64 border-r bg-black md:block">
      <div className="border-b px-6 py-4">
       <p className="text-xs uppercase tracking-wider text-violet-300/80">
  AssetFlow AI
</p>

<h1 className="mt-1 text-lg font-bold text-white">
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
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all duration-300",
                isActive
                  ? "bg-gradient-to-r from-amber-400/20 to-orange-400/20 text-amber-100 border border-orange-300/40 shadow-[0_0_20px_rgba(251,191,36,0.55)]"
                  : "text-zinc-300 hover:bg-white/10 hover:text-amber-100 hover:border-amber-300/20 hover:shadow-[0_0_12px_rgba(251,191,36,0.35)]"
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto border-t px-3 py-3">
        <button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent">
          <Settings className="h-4 w-4" />
          Settings
        </button>
      </div>
    </aside>
  );
}
