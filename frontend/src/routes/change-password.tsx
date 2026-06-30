import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";

import { PasswordField } from "@/components/password-field";
import { useAuth } from "@/lib/auth-context";
import { changePasswordRequest } from "@/features/auth/api";

export const Route = createFileRoute("/change-password")({
  component: ChangePassword,
});

function ChangePassword() {
  const { user, loading, refresh } = useAuth();
  const navigate = useNavigate();
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!loading && !user) void navigate({ to: "/login" });
  }, [user, loading, navigate]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (next !== confirm) { setError("Passwords don't match"); return; }
    setBusy(true);
    setError(null);
    try {
      await changePasswordRequest({ current_password: current, new_password: next });
      await refresh();
      void navigate({ to: "/dashboard" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to change password");
    } finally { setBusy(false); }
  };

  return (
    <div className="min-h-screen grid place-items-center p-6">
      <form onSubmit={onSubmit} className="card-surface p-6 w-full max-w-sm space-y-4">
        <div>
          <h2 className="text-xl font-semibold">Change password</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {user?.must_change_password ? "Set a new password to continue." : "Update your password."}
          </p>
        </div>
        {error && <div className="rounded-lg border border-critical/40 bg-critical/10 px-3 py-2 text-sm">{error}</div>}
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground">Current password</label>
          <PasswordField value={current} onChange={setCurrent} required autoComplete="current-password" />
        </div>
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground">New password</label>
          <PasswordField value={next} onChange={setNext} required autoComplete="new-password" />
        </div>
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground">Confirm new password</label>
          <PasswordField value={confirm} onChange={setConfirm} required autoComplete="new-password" />
        </div>
        <button disabled={busy} className="w-full h-10 rounded-lg bg-primary text-primary-foreground font-medium disabled:opacity-60">
          {busy ? "Saving…" : "Save password"}
        </button>
      </form>
    </div>
  );
}
