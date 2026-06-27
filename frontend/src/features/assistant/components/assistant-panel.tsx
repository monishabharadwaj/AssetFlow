import { useState } from "react";
import { Link } from "react-router-dom";
import { Bot, Loader2, Send } from "lucide-react";
import { useMutation } from "@tanstack/react-query";

import { assistantChat } from "../../intelligence/api/intelligence-api";
import { Button } from "../../../shared/components/ui/button";
import { Dialog } from "../../../shared/components/ui/dialog";
import { Input } from "../../../shared/components/ui/input";

const SUGGESTED_PROMPTS = [
  "Which assets require maintenance?",
  "Show high-risk assets",
  "What transferred recently?",
  "Which department owns the most assets?",
];

type AssistantPanelProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

function AssistantMessage({ text }: { text: string }) {
  const lines = text.split("\n").filter((line) => line.trim().length > 0);
  return (
    <div className="space-y-1.5">
      {lines.map((line, index) => {
        const trimmed = line.trim();
        if (trimmed.startsWith("•")) {
          return (
            <p key={`${index}-${trimmed}`} className="pl-1 leading-relaxed">
              {trimmed}
            </p>
          );
        }
        return (
          <p key={`${index}-${trimmed}`} className="leading-relaxed">
            {trimmed}
          </p>
        );
      })}
    </div>
  );
}

export function AssistantPanel({ open, onOpenChange }: AssistantPanelProps) {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<Array<{ role: "user" | "assistant"; text: string }>>([]);
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null);

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
      setHistory((prev) => [...prev, { role: "assistant", text: data.answer }]);
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange} title="AssetFlow Assistant">
      <div className="flex max-h-[70vh] flex-col gap-3">
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
                    <div className="mb-1 flex items-center gap-1 text-xs font-medium text-muted-foreground">
                      <Bot className="h-3 w-3" /> Assistant
                    </div>
                  ) : null}
                  {entry.role === "assistant" ? (
                    <AssistantMessage text={entry.text} />
                  ) : (
                    entry.text
                  )}
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

        {chat.data?.sources?.length ? (
          <div className="flex flex-wrap gap-2 border-t pt-2">
            {chat.data.sources.map((source) => (
              <Link
                key={source.asset_id}
                to={source.url}
                className="text-xs text-primary hover:underline"
                onClick={() => onOpenChange(false)}
              >
                {source.label}
              </Link>
            ))}
          </div>
        ) : null}

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
