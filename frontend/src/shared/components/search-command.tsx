import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search } from "lucide-react";

import { searchAssets } from "../../features/assets/api/assets-api";
import { Dialog } from "./ui/dialog";
import { Input } from "./ui/input";

type SearchCommandProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

type Result = { id: string; label: string; href: string; group: string };

export function SearchCommand({ open, onOpenChange }: SearchCommandProps) {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) {
      setQuery("");
      setResults([]);
    }
  }, [open]);

  useEffect(() => {
    const q = query.trim();
    if (q.length < 2) {
      setResults([]);
      return;
    }

    const timer = setTimeout(() => {
      setLoading(true);
      Promise.all([
        searchAssets({ page: 1, page_size: 6, asset_tag: q }),
        searchAssets({ page: 1, page_size: 6, name: q }),
      ])
        .then(([byTag, byName]) => {
          const assetMap = new Map<string, Result>();
          for (const asset of [...byTag.items, ...byName.items]) {
            assetMap.set(asset.id, {
              id: asset.id,
              label: `${asset.asset_tag} — ${asset.name}`,
              href: `/assets/${asset.id}`,
              group: "Assets",
            });
          }
          setResults([...assetMap.values()]);
        })
        .finally(() => setLoading(false));
    }, 250);

    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        onOpenChange(true);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onOpenChange]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange} title="Search">
      <div className="space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            className="pl-9"
            placeholder="Search assets, tags, employees…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
          />
        </div>
        {loading ? <p className="text-sm text-muted-foreground">Searching…</p> : null}
        <div className="max-h-64 space-y-1 overflow-y-auto">
          {results.map((result) => (
            <button
              key={`${result.group}-${result.id}`}
              type="button"
              className="flex w-full flex-col rounded-md px-3 py-2 text-left text-sm hover:bg-accent"
              onClick={() => {
                navigate(result.href);
                onOpenChange(false);
              }}
            >
              <span className="text-xs text-muted-foreground">{result.group}</span>
              <span>{result.label}</span>
            </button>
          ))}
          {!loading && query.length >= 2 && results.length === 0 ? (
            <p className="px-3 py-2 text-sm text-muted-foreground">No results</p>
          ) : null}
        </div>
        <p className="text-xs text-muted-foreground">Tip: press Ctrl+K / Cmd+K anywhere</p>
      </div>
    </Dialog>
  );
}
