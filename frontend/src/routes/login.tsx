import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";

import { PasswordField } from "@/components/password-field";
import { AssetFlowLogo } from "@/features/auth/components/assetflow-logo";
import { EnterpriseHero } from "@/features/auth/components/enterprise-hero";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";

export const Route = createFileRoute("/login")({
  component: LoginPage,
});

function SignInCard({
  email,
  password,
  error,
  submitting,
  onEmailChange,
  onPasswordChange,
  onSubmit,
}: {
  email: string;
  password: string;
  error: string | null;
  submitting: boolean;
  onEmailChange: (v: string) => void;
  onPasswordChange: (v: string) => void;
  onSubmit: (e: React.FormEvent) => void;
}) {
  return (
    <form
      onSubmit={onSubmit}
      className="w-full max-w-sm rounded-xl border border-border bg-card/90 backdrop-blur-md shadow-xl p-8 space-y-5"
    >
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
          onChange={(e) => onEmailChange(e.target.value)}
          autoComplete="email"
          className="w-full h-10 px-3 rounded-lg bg-background border border-border focus:outline-none focus:ring-2 focus:ring-ring/50"
        />
      </div>
      <div className="space-y-2">
        <label className="text-xs font-medium text-muted-foreground">Password</label>
        <PasswordField value={password} onChange={onPasswordChange} required autoComplete="current-password" />
      </div>
      <button
        type="submit"
        disabled={submitting}
        className="w-full h-10 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-60 glow-primary"
      >
        {submitting ? "Signing in…" : "Sign in"}
      </button>
    </form>
  );
}

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

  const signInProps = {
    email,
    password,
    error,
    submitting,
    onEmailChange: setEmail,
    onPasswordChange: setPassword,
    onSubmit,
  };

  return (
    <div className="relative min-h-screen bg-background">
      {/* Desktop: full-viewport hero; sign-in floats on the right */}
      <div
        className="hidden lg:flex flex-col justify-between min-h-screen p-12 xl:p-14 pr-[22rem] xl:pr-[26rem] bg-gradient-to-br from-[oklch(0.22_0.05_285)] via-[oklch(0.19_0.03_270)] to-[oklch(0.16_0.02_240)]"
      >
        <div className="flex items-center gap-3">
          <AssetFlowLogo size="sm" />
          <div>
            <div className="text-lg font-bold tracking-wide gradient-text">ASSETFLOW AI</div>
            <div className="text-xs text-muted-foreground tracking-[0.2em] font-medium">ENTERPRISE</div>
          </div>
        </div>
        <div className="space-y-6 flex-1 flex flex-col justify-center">
          <div className="space-y-4">
            <h1
              className="text-[2.75rem] xl:text-[3rem] leading-[1.12] font-medium text-foreground max-w-xl"
              style={{ fontFamily: "'Fraunces', Georgia, serif" }}
            >
              Fleet lifecycle control<br />for operations teams.
            </h1>
            <div className="text-muted-foreground max-w-lg text-lg leading-relaxed space-y-2">
              <p>
                Register assets, assign them to people, schedule maintenance, and read health scores —
                scoped to your role and department in one console.
              </p>
              <p>
                AI health scoring and drift monitoring across the fleet — act before failures hit operations.
              </p>
              <p>
                Tool-grounded assistant and executive reports for leaders — maintenance, capital, and cost in plain English.
              </p>
            </div>
            <ul className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-muted-foreground/90 tracking-wide pt-1">
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

      <div className="hidden lg:block absolute right-8 xl:right-12 top-1/2 -translate-y-1/2 z-20 w-[24rem]">
        <SignInCard {...signInProps} />
      </div>

      {/* Mobile: centered card + brand */}
      <div className="lg:hidden flex flex-col items-center justify-center min-h-screen p-6 gap-8">
        <div className="flex items-center gap-3">
          <AssetFlowLogo size="sm" />
          <div>
            <div className="text-lg font-bold tracking-wide gradient-text">ASSETFLOW AI</div>
            <div className="text-xs text-muted-foreground tracking-[0.2em] font-medium">ENTERPRISE</div>
          </div>
        </div>
        <SignInCard {...signInProps} />
      </div>
    </div>
  );
}
