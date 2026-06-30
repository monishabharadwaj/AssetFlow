import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";

import { PasswordField } from "@/components/password-field";
import { EnterpriseHero } from "@/features/auth/components/enterprise-hero";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";

export const Route = createFileRoute("/login")({
  component: LoginPage,
});

function LoginPage() {
  const { login, user, loading } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && user) {
      void navigate({ to: user.must_change_password ? "/change-password" : "/dashboard" });
    }
  }, [user, loading, navigate]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const me = await login(email, password);
      void navigate({ to: me.must_change_password ? "/change-password" : "/dashboard" });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : (err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-background">
      <div className="hidden lg:flex flex-col justify-between p-12 bg-gradient-to-br from-[oklch(0.22_0.05_285)] via-[oklch(0.19_0.03_270)] to-[oklch(0.16_0.02_240)] border-r border-border">
        <div className="flex items-center gap-2">
          <div className="size-9 rounded-lg bg-gradient-to-br from-[oklch(0.65_0.22_285)] to-[oklch(0.6_0.2_245)] grid place-items-center text-white font-bold glow-primary">A</div>
          <div>
            <div className="text-sm font-semibold gradient-text">ASSETFLOW AI</div>
            <div className="text-[10px] text-muted-foreground tracking-wider">ENTERPRISE</div>
          </div>
        </div>
        <div className="space-y-5">
          <div className="space-y-3">
            <h1
              className="text-[2.35rem] leading-[1.15] font-medium text-foreground"
              style={{ fontFamily: "'Fraunces', Georgia, serif" }}
            >
              Fleet lifecycle control<br />for operations teams.
            </h1>
            <p className="text-muted-foreground max-w-md text-[15px] leading-relaxed">
              Register assets, assign them to people, schedule maintenance, and read health scores —
              scoped to your role and department in one console.
            </p>
            <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground/90 tracking-wide">
              <li>Lifecycle</li>
              <li className="text-border">·</li>
              <li>Intelligence</li>
              <li className="text-border">·</li>
              <li>Reporting</li>
            </ul>
          </div>
          <EnterpriseHero />
        </div>
        <p className="text-xs text-muted-foreground">© AssetFlow AI</p>
      </div>

      <div className="flex items-center justify-center p-8">
        <form onSubmit={onSubmit} className="w-full max-w-sm space-y-5">
          <div>
            <h2 className="text-2xl font-semibold">Sign in</h2>
            <p className="text-sm text-muted-foreground mt-1">Access your operations console.</p>
          </div>
          {error && (
            <div className="rounded-lg border border-critical/40 bg-critical/10 px-3 py-2 text-sm text-[oklch(0.85_0.18_18)]">
              {error}
            </div>
          )}
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              className="w-full h-10 px-3 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-ring/50"
            />
          </div>
          <div className="space-y-2">
            <label className="text-xs font-medium text-muted-foreground">Password</label>
            <PasswordField value={password} onChange={setPassword} required autoComplete="current-password" />
          </div>
          <button
            type="submit"
            disabled={submitting}
            className="w-full h-10 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-60 glow-primary"
          >
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
