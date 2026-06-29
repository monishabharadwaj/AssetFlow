import { fetchDashboardSummary } from "@/features/dashboard/api";
import type { User } from "@/lib/types/ui";
import { assistantScopeBadge } from "@/lib/format-scope";

export function normalizeAssistantMessage(message: string): string {
  return message
    .replace(/\bneed attention\b/gi, "needs attention")
    .replace(/\brequire maintenance\b/gi, "requires maintenance");
}

export function isGenericAssistantFallback(answer: string): boolean {
  const lower = answer.toLowerCase();
  return (
    lower.includes("not sure what you need") ||
    lower.includes("i can help with:") ||
    lower.includes("try a suggested prompt")
  );
}

export function isAttentionQuery(message: string): boolean {
  const lower = message.toLowerCase();
  return (
    /\b(needs?|require[sd]?)\s+attention\b/.test(lower) ||
    /\battention\s+this\s+week\b/.test(lower) ||
    /\bhigh[\s-]?risk\b/.test(lower)
  );
}

export async function buildAttentionFallback(
  user: User | null | undefined,
): Promise<{ text: string; sources: { id: string; tag?: string; name?: string }[] }> {
  const scope = assistantScopeBadge(user);
  const summary = await fetchDashboardSummary();
  const items = summary.attention_items ?? [];
  const sources = items
    .filter((i) => i.asset_id)
    .slice(0, 8)
    .map((i) => ({
      id: String(i.asset_id),
      tag: i.subtitle?.split(" · ")[0] ?? i.title,
      name: i.title,
    }));

  if (items.length === 0) {
    const due = summary.kpis.maintenance_due;
    if (due > 0) {
      return {
        text: `For ${scope}: ${due} maintenance item${due === 1 ? "" : "s"} due. Check the Maintenance page or Operations Center for details.`,
        sources: [],
      };
    }
    return {
      text: `For ${scope}: no assets currently flagged for attention. Fleet looks clear.`,
      sources: [],
    };
  }

  const lines = items.slice(0, 8).map((i) => {
    const detail = i.subtitle ? ` — ${i.subtitle}` : "";
    return `• ${i.title}${detail} (${i.severity})`;
  });

  return {
    text: `Assets needing attention (${scope}):\n\n${lines.join("\n")}`,
    sources,
  };
}
