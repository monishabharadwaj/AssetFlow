import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bot, Loader2, Send, Trash2 } from "lucide-react";
import { useMutation } from "@tanstack/react-query";

import { assistantChat } from "../../intelligence/api/intelligence-api";
import { Button } from "../../../shared/components/ui/button";
import { Dialog } from "../../../shared/components/ui/dialog";
import { Input } from "../../../shared/components/ui/input";

const SUGGESTED_PROMPTS = [
  "Which department owns the most assets?",
  "Which assets are at high risk?",
  "Which assets require maintenance this week?",
  "Which laptops belong to Engineering?",
  "Which warranties expire this month?",
];

/** Human-readable labels for backend tool names (shown as small badges). */
const TOOL_LABELS: Record<string, string> = {
  get_dashboard_summary: "Fleet overview",
  get_department_ranking: "Department ranking",
  get_department_maintenance_ranking: "Maintenance by dept",
  get_maintenance_this_week: "Maintenance this week",
  get_warranty_this_month: "Warranty this month",
  get_assets_by_department_and_type: "Dept + type filter",
  get_high_risk_by_type: "High risk by type",
  get_asset_department: "Asset department",
  get_asset_assignee: "Asset assignee",
  get_clarification: "Clarify",
  get_high_risk_assets: "High-risk assets",
  get_healthy_assets: "Healthy assets",
  get_worst_health_assets: "Lowest health",
  get_maintenance_recommendations: "AI recommendations",
  get_overdue_maintenance: "Overdue maintenance",
  get_assets_in_maintenance: "In maintenance",
  get_recent_allocations: "Recent assignments",
  get_recent_completed_maintenance: "Completed maintenance",
  get_recent_transfers: "Recent transfers",
  get_warranty_expiring: "Warranty expiring",
  get_fleet_counts: "Fleet counts",
  get_department_assets: "Department assets",
  get_employee_assets: "Employee assets",
  get_assets_by_status: "Assets by status",
  get_asset_health_detail: "Asset health",
  search_assets: "Asset search",
  get_help: "Help",
};

type AssistantPanelProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

type HistoryItem = {
  role: "user" | "assistant";
  text: string;
  toolsUsed?: string[];
  sources?: Array<{
    label: string;
    asset_id: string;
    url: string;
  }>;
};

function AssistantMessage({ text }: { text: string }) {
  const lines = text.split("\n");
  const renderedElements: React.ReactNode[] = [];
  let currentList: React.ReactNode[] = [];

  const flushList = (keyPrefix: string | number) => {
    if (currentList.length > 0) {
      renderedElements.push(
        <ul key={`list-${keyPrefix}`} className="list-disc pl-5 space-y-1 my-1.5">
          {currentList}
        </ul>
      );
      currentList = [];
    }
  };

  const parseInline = (lineText: string) => {
    const parts = lineText.split(/(\*\*.*?\*\*|`.*?`)/g);
    return parts.map((part, partIdx) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return <strong key={partIdx}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith("`") && part.endsWith("`")) {
        return (
          <code key={partIdx} className="bg-muted px-1.5 py-0.5 rounded text-[11px] font-mono border">
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  };

  lines.forEach((line, index) => {
    const trimmed = line.trim();
    const isNumbered = /^\d+\.\s/.test(trimmed);
    const isBullet = !isNumbered && (trimmed.startsWith("•") || trimmed.startsWith("-") || trimmed.startsWith("*"));

    if (isNumbered) {
      const displayLine = trimmed.replace(/^\d+\.\s*/, "");
      currentList.push(
        <li key={`li-${index}`} className="leading-relaxed text-sm list-decimal">
          {parseInline(displayLine)}
        </li>
      );
    } else if (isBullet) {
      const displayLine = trimmed.replace(/^[•\-\*]\s*/, "");
      currentList.push(
        <li key={`li-${index}`} className="leading-relaxed text-sm">
          {parseInline(displayLine)}
        </li>
      );
    } else {
      flushList(index);
      if (trimmed.startsWith("###")) {
        renderedElements.push(
          <h4 key={`h4-${index}`} className="text-sm font-semibold mt-2.5 mb-1">
            {trimmed.replace(/^###\s*/, "")}
          </h4>
        );
      } else if (trimmed.startsWith("##")) {
        renderedElements.push(
          <h3 key={`h3-${index}`} className="text-base font-semibold mt-3.5 mb-1.5">
            {trimmed.replace(/^##\s*/, "")}
          </h3>
        );
      } else if (trimmed.length > 0) {
        renderedElements.push(
          <p key={`p-${index}`} className="leading-relaxed text-sm my-1">
            {parseInline(trimmed)}
          </p>
        );
      } else {
        renderedElements.push(<div key={`br-${index}`} className="h-1.5" />);
      }
    }
  });

  flushList("final");

  return <div className="space-y-0.5">{renderedElements}</div>;
}

export function AssistantPanel({ open, onOpenChange }: AssistantPanelProps) {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>(() => {
    try {
      const saved = localStorage.getItem("assetflow_chat_history");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null);

  useEffect(() => {
    try {
      localStorage.setItem("assetflow_chat_history", JSON.stringify(history));
    } catch (e) {
      console.error("Failed to save history to localStorage", e);
    }
  }, [history]);

  const chat = useMutation({
    mutationFn: (variables: string) => {
      const formattedHistory = history.map((item) => ({
        role: item.role,
        content: item.text,
      }));
      return assistantChat({ message: variables, history: formattedHistory });
    },
    onMutate: (variables) => {
      setHistory((prev) => [...prev, { role: "user", text: variables }]);
      setMessage("");
      setPendingPrompt(variables);
    },
    onSuccess: (data) => {
      setHistory((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          toolsUsed: data.tools_used,
          sources: data.sources,
        },
      ]);
      setPendingPrompt(null);
    },
    onError: () => {
      setPendingPrompt(null);
    },
  });

  const submitMessage = (value: string) => {
    const trimmed = value.trim();
    if (!trimmed || chat.isPending) return;
    void chat.mutate(trimmed);
  };

  const send = () => submitMessage(message);

  const clearChat = () => {
    setHistory([]);
    try {
      localStorage.removeItem("assetflow_chat_history");
    } catch {}
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange} title="AssetFlow Assistant">
      <div className="flex max-h-[70vh] flex-col gap-3">
        <div className="flex items-center justify-between border-b pb-2">
          <span className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">AI Operations Assistant</span>
          {history.length > 0 ? (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="h-auto p-0 text-xs text-rose-600 hover:text-rose-700 hover:bg-transparent flex items-center gap-1"
              onClick={clearChat}
            >
              <Trash2 className="h-3.5 w-3.5" />
              Clear chat history
            </Button>
          ) : null}
        </div>

        <div className="flex-1 space-y-3 overflow-y-auto pr-1">
          {history.length === 0 && !chat.isPending ? (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">
                Ask about assets, maintenance, risk, fleet counts, and recent operations.
              </p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTED_PROMPTS.map((prompt) => (
                  <Button
                    key={prompt}
                    type="button"
                    variant="secondary"
                    size="sm"
                    disabled={chat.isPending}
                    onClick={() => submitMessage(prompt)}
                  >
                    {chat.isPending && pendingPrompt === prompt ? (
                      <Loader2 className="mr-1 h-3 w-3 animate-spin" />
                    ) : null}
                    {prompt}
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            <>
              {history.map((entry, i) => (
                <div
                  key={`${entry.role}-${i}`}
                  className={
                    entry.role === "user"
                      ? "ml-8 rounded-lg bg-primary/10 p-3 text-sm"
                      : "mr-8 rounded-lg border bg-card p-3 text-sm"
                  }
                >
                  {entry.role === "assistant" ? (
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <span className="flex items-center gap-1 text-xs font-medium text-muted-foreground">
                        <Bot className="h-3 w-3" /> Assistant
                      </span>
                      {entry.toolsUsed?.length ? (
                        <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                          {TOOL_LABELS[entry.toolsUsed[0]] ?? entry.toolsUsed[0]}
                        </span>
                      ) : null}
                    </div>
                  ) : null}
                  {entry.role === "assistant" ? (
                    <AssistantMessage text={entry.text} />
                  ) : (
                    entry.text
                  )}

                  {entry.role === "assistant" && entry.sources?.length ? (
                    <div className="mt-2.5 flex flex-wrap gap-1.5 border-t pt-2">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-muted-foreground mr-1 self-center">
                        Sources:
                      </span>
                      {entry.sources.map((source) => (
                        <Link
                          key={source.asset_id}
                          to={source.url}
                          className="inline-flex items-center rounded bg-primary/5 px-2 py-0.5 text-xs text-primary hover:bg-primary/10 border border-primary/10"
                          onClick={() => onOpenChange(false)}
                        >
                          {source.label}
                        </Link>
                      ))}
                    </div>
                  ) : null}
                </div>
              ))}
              {chat.isPending ? (
                <div className="mr-8 flex items-center gap-2 rounded-lg border bg-card p-3 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Thinking…
                </div>
              ) : null}
            </>
          )}
          {chat.isError ? (
            <p className="text-sm text-rose-600">
              {chat.error instanceof Error ? chat.error.message : "Assistant request failed"}
            </p>
          ) : null}
        </div>

        <div className="flex gap-2 border-t pt-3">
          <Input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask AssetFlow AI…"
            disabled={chat.isPending}
            onKeyDown={(e) => {
              if (e.key === "Enter") send();
            }}
          />
          <Button type="button" size="sm" disabled={chat.isPending} onClick={send}>
            {chat.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </Dialog>
  );
}
