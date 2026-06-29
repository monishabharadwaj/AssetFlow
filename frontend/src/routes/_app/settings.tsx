import { createFileRoute, Link } from "@tanstack/react-router";
import { useAuth } from "@/lib/auth-context";
import { Card, CardHeader, Pill } from "@/components/ui-bits";
import { guardRoute } from "@/lib/route-guards";

export const Route = createFileRoute("/_app/settings")({
  beforeLoad: () => guardRoute("/settings"),
  component: SettingsPage,
});

function SettingsPage() {
  const { user } = useAuth();
  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Profile and preferences</p>
      </div>

      <Card>
        <CardHeader title="Profile" />
        <div className="grid grid-cols-2 gap-4">
          <Field label="Full name" value={user?.full_name ?? "—"} />
          <Field label="Email" value={user?.email ?? "—"} />
          <Field label="Role" value={<Pill>{user?.role ?? "—"}</Pill>} />
          <Field label="Department" value={user?.department_name ?? "—"} />
          {user?.job_title && <Field label="Job title" value={user.job_title} />}
          {user?.employee_code && <Field label="Employee ID" value={user.employee_code} />}
        </div>
      </Card>

      <Card>
        <CardHeader title="Security" subtitle="Update your password" />
        <Link to="/change-password" className="h-9 px-3 inline-flex items-center rounded-lg border border-border hover:bg-accent/40 text-sm">Change password</Link>
      </Card>
    </div>
  );
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <div className="text-[11px] uppercase tracking-wider text-muted-foreground">{label}</div>
      <div className="text-sm mt-1">{value}</div>
    </div>
  );
}
