import { Link, useRouter, useRouterState } from "@tanstack/react-router";
import {
  LayoutDashboard,
  Boxes,
  Wrench,
  Building2,
  Users,
  FileBarChart2,
  Settings,
  Bell,
  Search,
  Sparkles,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState, type ReactNode } from "react";

import { mapNotifications } from "@/lib/adapters/notifications";
import {
  buildAttentionFallback,
  isAttentionQuery,
  isGenericAssistantFallback,
  normalizeAssistantMessage,
} from "@/lib/assistant-fallback";
import { useAuth } from "@/lib/auth-context";
import { assistantScopeBadge } from "@/lib/format-scope";
import { canAccessNav } from "@/features/auth/permissions";
import { fetchNotifications } from "@/features/operations/api";
import { useMarkAllNotificationsRead, useMarkNotificationRead } from "@/features/operations/hooks";
import { cn } from "@/lib/utils";
import { Pill, Skeleton } from "@/components/ui-bits";
import { UserProfileMenu } from "@/features/auth/components/user-profile-menu";
import { api } from "@/lib/api";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";

interface NavItem {
  label: string;
  to: string;
  icon: typeof LayoutDashboard;
}

const NAV: NavItem[] = [
  { label: "Operations", to: "/dashboard", icon: LayoutDashboard },
  { label: "Assets", to: "/assets", icon: Boxes },
  { label: "Maintenance", to: "/maintenance", icon: Wrench },
  { label: "Departments", to: "/departments", icon: Building2 },
  { label: "Employees", to: "/employees", icon: Users },
  { label: "Reports", to: "/reports", icon: FileBarChart2 },
  { label: "Settings", to: "/settings", icon: Settings },
];

export function AppShell({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const [assistantOpen, setAssistantOpen] = useState(false);
  const { user, logout } = useAuth();
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <div className="min-h-screen flex w-full bg-background">
      {/* Sidebar */}
      <aside
        className={cn(
          "shrink-0 border-r border-sidebar-border bg-sidebar flex flex-col transition-[width] duration-200",
          collapsed ? "w-16" : "w-60",
        )}
      >
        <div className="h-16 flex items-center gap-2 px-4 border-b border-sidebar-border">
          <div className="size-8 rounded-lg bg-gradient-to-br from-[oklch(0.65_0.22_285)] to-[oklch(0.6_0.2_245)] grid place-items-center text-white text-sm font-bold glow-primary">
            A
          </div>
          {!collapsed && (
            <div className="leading-tight">
              <div className="text-sm font-semibold gradient-text">ASSETFLOW</div>
              <div className="text-[10px] text-muted-foreground tracking-wider">ENTERPRISE</div>
            </div>
          )}
        </div>

        <nav className="flex-1 py-4 px-2 space-y-0.5">
          {NAV.filter((item) => canAccessNav(user?.role, item.to)).map((item) => {
            const active = pathname === item.to || pathname.startsWith(item.to + "/");
            const Icon = item.icon;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-sidebar-accent text-foreground"
                    : "text-muted-foreground hover:bg-sidebar-accent/40 hover:text-foreground",
                )}
              >
                <Icon className="size-4 shrink-0" />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        <div className="p-2 border-t border-sidebar-border space-y-1">
          <button
            onClick={() => setCollapsed((c) => !c)}
            className="w-full flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-sidebar-accent/40 hover:text-foreground"
          >
            {collapsed ? <ChevronRight className="size-4" /> : <ChevronLeft className="size-4" />}
            {!collapsed && <span>Collapse</span>}
          </button>
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-sidebar-accent/40 hover:text-foreground"
          >
            <LogOut className="size-4" />
            {!collapsed && <span>Sign out</span>}
          </button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <TopBar onOpenAssistant={() => setAssistantOpen(true)} />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-[1600px] mx-auto p-6 lg:p-8">{children}</div>
        </main>
      </div>

      <AssistantPanel open={assistantOpen} onClose={() => setAssistantOpen(false)} />
    </div>
  );
}

function TopBar({ onOpenAssistant }: { onOpenAssistant: () => void }) {
  const { user } = useAuth();
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);
  const markRead = useMarkNotificationRead();
  const markAllRead = useMarkAllNotificationsRead();

  const { data: notifResponse } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => fetchNotifications(20),
    refetchInterval: 60_000,
  });
  const notifItems = mapNotifications(notifResponse?.items ?? []);
  const unread = notifResponse?.unread_count ?? notifItems.filter((n) => !n.read).length;
  const canMarkAll = user?.role !== "VIEWER";

  useEffect(() => {
    if (!notifOpen) return;
    const onPointerDown = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) {
        setNotifOpen(false);
      }
    };
    document.addEventListener("mousedown", onPointerDown);
    return () => document.removeEventListener("mousedown", onPointerDown);
  }, [notifOpen]);

  const handleNotifClick = (n: (typeof notifItems)[0]) => {
    if (!n.read) markRead.mutate(n.id);
    if (n.asset_id) {
      setNotifOpen(false);
      void router.navigate({ to: "/assets/$id", params: { id: n.asset_id } });
    }
  };

  return (
    <header className="h-16 border-b border-border bg-card/50 backdrop-blur sticky top-0 z-30">
      <div className="h-full px-6 flex items-center gap-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (search.trim()) router.navigate({ to: "/assets", search: { q: search.trim() } as never });
          }}
          className="flex-1 max-w-xl relative"
        >
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search assets, employees, departments…"
            className="w-full h-10 pl-10 pr-3 rounded-lg bg-background/60 border border-border text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring/50"
          />
        </form>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onOpenAssistant}
            className="h-10 px-3 rounded-lg border border-border hover:bg-accent/40 text-sm flex items-center gap-2"
          >
            <Sparkles className="size-4 text-[oklch(0.78_0.16_285)]" />
            <span className="hidden md:inline">Assistant</span>
          </button>
          <div className="relative" ref={notifRef}>
          <button
            type="button"
            onClick={() => setNotifOpen((o) => !o)}
            aria-expanded={notifOpen}
            aria-label="Notifications"
            className="relative h-10 w-10 rounded-lg border border-border hover:bg-accent/40 grid place-items-center"
          >
            <Bell className="size-4" />
            {unread > 0 && (
              <span className="absolute -top-1 -right-1 size-5 rounded-full bg-critical text-[10px] font-bold grid place-items-center text-white">
                {unread > 9 ? "9+" : unread}
              </span>
            )}
          </button>
          {notifOpen && (
            <div className="absolute right-0 top-12 z-40 w-80 max-h-96 overflow-y-auto rounded-xl border border-border bg-card shadow-lg">
              <div className="flex items-center justify-between px-4 py-3 border-b border-border">
                <span className="text-sm font-semibold">Notifications</span>
                {unread > 0 && canMarkAll && (
                  <button
                    type="button"
                    className="text-xs text-muted-foreground hover:text-foreground"
                    onClick={() => markAllRead.mutate()}
                  >
                    Mark all read
                  </button>
                )}
              </div>
              {notifItems.length === 0 ? (
                <div className="px-4 py-8 text-center text-sm text-muted-foreground">No notifications</div>
              ) : (
                <ul>
                  {notifItems.map((n) => (
                    <li
                      key={n.id}
                      className={cn(
                        "px-4 py-3 border-b border-border text-sm cursor-pointer hover:bg-accent/30",
                        !n.read && "bg-primary/5",
                      )}
                      onClick={() => handleNotifClick(n)}
                    >
                      <div className="font-medium">{n.title}</div>
                      {n.body && <div className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{n.body}</div>}
                      {n.asset_id && (
                        <div className="text-[11px] text-primary/80 mt-1">View asset →</div>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
          </div>
          <UserProfileMenu />
        </div>
      </div>
    </header>
  );
}

function AssistantPanel({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { user } = useAuth();
  const scopeBadge = assistantScopeBadge(user);
  type ChatMsg = {
    role: "user" | "assistant";
    content: string;
    sources?: { id: string | number; tag?: string; name?: string }[];
  };
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async (msg: string) => {
    const normalized = normalizeAssistantMessage(msg);
    const next = [...messages, { role: "user" as const, content: msg }];
    setMessages(next);
    setInput("");
    setLoading(true);
    try {
      const res = await api<{ answer: string; sources?: { label: string; asset_id: string; url: string }[] }>(
        "/assistant/chat",
        { method: "POST", body: { message: normalized, history: messages } },
      );

      let answer = res.answer;
      let sources: ChatMsg["sources"] = res.sources?.map((s) => ({ id: s.asset_id, tag: s.label, name: s.label }));

      if (isGenericAssistantFallback(answer) && isAttentionQuery(normalized)) {
        try {
          const fallback = await buildAttentionFallback(user);
          answer = fallback.text;
          sources = fallback.sources;
        } catch {
          answer = `For ${scopeBadge}: I couldn't load attention data right now. Check the Operations Center "Needs Attention" panel.`;
        }
      }

      setMessages([...next, {
        role: "assistant",
        content: answer,
        sources,
      }]);
    } catch (e) {
      setMessages([...next, { role: "assistant", content: `Couldn't reach assistant: ${(e as Error).message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const suggested = [
    "Which assets requires maintenance this week?",
    "Which department has the most maintenance requests?",
    "What maintenance is overdue?",
  ];

  return (
    <Sheet open={open} onOpenChange={(o) => !o && onClose()}>
      <SheetContent side="right" className="w-full sm:max-w-md p-0 flex flex-col gap-0">
        <SheetHeader className="h-16 flex flex-row items-center justify-between px-5 border-b border-border space-y-0">
          <div className="flex items-center gap-2">
            <Sparkles className="size-4 text-[oklch(0.78_0.16_285)]" />
            <SheetTitle className="text-base">Assistant</SheetTitle>
          </div>
          <Pill className="text-[10px]">{scopeBadge}</Pill>
        </SheetHeader>
        <div className="flex-1 overflow-y-auto p-5 space-y-3 min-h-0">
          {messages.length === 0 && (
            <div className="space-y-2">
              <p className="text-xs text-muted-foreground">Suggested prompts · {scopeBadge}</p>
              {suggested.map((p) => (
                <button
                  key={p}
                  type="button"
                  disabled={loading}
                  onClick={() => void send(p)}
                  className="w-full text-left text-sm rounded-lg border border-border px-3 py-2 hover:bg-accent/40 disabled:opacity-50"
                >
                  {p}
                </button>
              ))}
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={cn("text-sm rounded-lg px-3 py-2", m.role === "user" ? "bg-primary/15 ml-8" : "bg-muted/40 mr-8")}>
              {m.role === "assistant" && (
                <div className="text-[10px] uppercase tracking-wider text-muted-foreground mb-1.5">{scopeBadge}</div>
              )}
              <div className="whitespace-pre-wrap">{m.content}</div>
              {m.sources && m.sources.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {m.sources.map((s) => (
                    <Link key={String(s.id)} to="/assets/$id" params={{ id: String(s.id) }} className="text-[11px] underline text-muted-foreground hover:text-foreground">
                      {s.tag ?? s.name ?? `#${s.id}`}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="mr-8 space-y-2 rounded-lg bg-muted/40 px-3 py-3">
              <Pill>Thinking…</Pill>
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-4/5" />
            </div>
          )}
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (input.trim() && !loading) void send(input.trim());
          }}
          className="p-4 border-t border-border flex gap-2 shrink-0"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="Ask about assets, maintenance, risks…"
            className="flex-1 h-10 px-3 rounded-lg bg-background border border-border text-sm focus:outline-none focus:ring-2 focus:ring-ring/50 disabled:opacity-60"
          />
          <Button type="submit" className="h-10" disabled={loading || !input.trim()}>Send</Button>
        </form>
      </SheetContent>
    </Sheet>
  );
}
