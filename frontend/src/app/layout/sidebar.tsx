import { BarChart3, Building2, ClipboardList, LayoutGrid, LogOut, Settings, Users } from "lucide-react";
import { NavLink } from "react-router-dom";

import { useAuth } from "../../features/auth/auth-context";
import { visibleNavItems } from "../../features/auth/permissions";
import { cn } from "../../shared/lib/utils";
import { Button } from "../../shared/components/ui/button";

export function Sidebar() {
  const { user, logout } = useAuth();
  const navItems = visibleNavItems(user?.role);

  return (
    <aside className="hidden w-64 border-r bg-card md:flex md:flex-col">
      <div className="border-b px-6 py-4">
        <p className="text-xs uppercase tracking-wide text-muted-foreground">AssetFlow AI</p>
        <h1 className="mt-1 text-lg font-semibold">Operations Console</h1>
        {user ? (
          <p className="mt-2 text-xs text-muted-foreground">
            {user.full_name} · {user.role}
          </p>
        ) : null}
      </div>
      <nav className="space-y-1 px-3 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-accent",
                isActive ? "bg-accent text-foreground" : "text-muted-foreground",
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto border-t px-3 py-3">
        {user?.role === "ADMIN" ? (
          <button
            type="button"
            className="mb-2 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-accent"
          >
            <Settings className="h-4 w-4" />
            Settings
          </button>
        ) : null}
        <Button type="button" variant="ghost" className="w-full justify-start" onClick={logout}>
          <LogOut className="mr-2 h-4 w-4" />
          Sign out
        </Button>
      </div>
    </aside>
  );
}
