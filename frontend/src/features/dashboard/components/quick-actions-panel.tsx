import { Link } from "@tanstack/react-router";
import { Boxes, Building2, Users, Wrench } from "lucide-react";

import { Card, CardHeader } from "@/components/ui-bits";
import { canAccessNav } from "@/features/auth/permissions";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";

const ACTIONS = [
  { label: "Assets", to: "/assets", icon: Boxes, description: "Search and manage fleet" },
  { label: "Maintenance", to: "/maintenance", icon: Wrench, description: "Work queue & scheduling" },
  { label: "Departments", to: "/departments", icon: Building2, description: "Org structure" },
  { label: "Employees", to: "/employees", icon: Users, description: "Employee directory" },
] as const;

export function QuickActionsPanel() {
  const { user } = useAuth();
  const visible = ACTIONS.filter((a) => canAccessNav(user?.role, a.to));

  if (visible.length === 0) return null;

  return (
    <Card>
      <CardHeader title="Quick actions" subtitle="Jump to common operations" />
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {visible.map((action) => {
          const Icon = action.icon;
          return (
            <Link
              key={action.to}
              to={action.to}
              className={cn(
                "rounded-xl border border-border p-4 hover:bg-accent/30 transition-colors",
                "flex flex-col gap-2",
              )}
            >
              <div className="size-9 rounded-lg bg-primary/15 grid place-items-center text-[oklch(0.82_0.18_285)]">
                <Icon className="size-4" />
              </div>
              <div className="font-medium text-sm">{action.label}</div>
              <div className="text-xs text-muted-foreground">{action.description}</div>
            </Link>
          );
        })}
      </div>
    </Card>
  );
}
