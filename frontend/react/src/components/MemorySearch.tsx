import { useState } from "react";
import { api } from "@/lib/api";

export function MemorySearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Array<Record<string, unknown>>>([]);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const hits = await api.memory.search(query);
      setResults(hits);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl space-y-4">
      <div className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
          placeholder="Search semantic memory…"
          className="flex-1 bg-odin-bg border border-odin-border rounded-lg px-3 py-2 text-sm"
        />
        <button
          onClick={search}
          disabled={loading}
          className="px-4 py-2 rounded-lg bg-odin-accent/20 text-odin-accent text-sm"
        >
          Search
        </button>
      </div>
      <ul className="space-y-2">
        {results.map((r, i) => (
          <li key={i} className="rounded border border-odin-border bg-odin-panel p-3 text-sm">
            <p>{String(r.content ?? "")}</p>
            <p className="text-xs text-odin-muted mt-1 font-mono">{String(r.id ?? "")}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}
