import { Link } from "@tanstack/react-router";
import { LogOut, Settings } from "lucide-react";

import { Pill } from "@/components/ui-bits";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";

export function UserProfileMenu({ className }: { className?: string }) {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          className={cn(
            "h-10 pl-2 pr-3 rounded-lg border border-border bg-card flex items-center gap-2 hover:bg-accent/30 transition-colors",
            className,
          )}
        >
          <div className="size-7 rounded-full bg-gradient-to-br from-[oklch(0.65_0.22_285)] to-[oklch(0.6_0.2_245)] grid place-items-center text-xs font-semibold text-white">
            {(user.full_name ?? "U").slice(0, 1).toUpperCase()}
          </div>
          <div className="hidden sm:block leading-tight text-left">
            <div className="text-xs font-medium">{user.full_name}</div>
            <div className="text-[10px] text-muted-foreground uppercase tracking-wide">{user.role}</div>
          </div>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-72">
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col gap-1">
            <span className="font-semibold text-sm">{user.full_name}</span>
            <span className="text-xs text-muted-foreground">{user.email}</span>
            <Pill className="w-fit mt-1">{user.role}</Pill>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <div className="px-2 py-1.5 text-xs space-y-2">
          <div>
            <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Department</div>
            <div className="mt-0.5">{user.department_name ?? "—"}</div>
          </div>
          {user.job_title && (
            <div>
              <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Job title</div>
              <div className="mt-0.5">{user.job_title}</div>
            </div>
          )}
          {user.employee_code && (
            <div>
              <div className="text-[10px] uppercase tracking-wider text-muted-foreground">Employee ID</div>
              <div className="mt-0.5 font-mono">{user.employee_code}</div>
            </div>
          )}
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <Link to="/settings" className="flex items-center gap-2 cursor-pointer">
            <Settings className="size-4" /> Settings
          </Link>
        </DropdownMenuItem>
        <DropdownMenuItem
          className="text-destructive focus:text-destructive cursor-pointer"
          onClick={() => logout()}
        >
          <LogOut className="size-4 mr-2" /> Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
