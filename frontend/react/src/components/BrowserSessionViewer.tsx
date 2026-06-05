export function BrowserSessionViewer({ session }: { session: Record<string, unknown> | null }) {
  if (!session) {
    return <p className="text-odin-muted text-sm">No browser session analyzed.</p>;
  }
  const tabs = (session.tabs as Array<Record<string, unknown>>) || [];
  return (
    <div className="space-y-4 max-w-2xl">
      <p className="text-sm text-slate-200">{String(session.insight ?? "")}</p>
      <p className="text-xs text-odin-muted">
        Topics: {((session.research_topics as string[]) || []).join(", ") || "—"}
      </p>
      <ul className="space-y-1 text-xs font-mono max-h-64 overflow-y-auto">
        {tabs.map((t, i) => (
          <li key={i} className="truncate text-odin-muted">
            {String(t.title || t.url)}
          </li>
        ))}
      </ul>
    </div>
  );
}
