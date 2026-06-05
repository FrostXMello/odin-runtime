export function VoiceSessionConsole({
  sessions,
}: {
  sessions: Array<{ id: string; state?: string; latency_ms?: number }>;
}) {
  if (!sessions.length) {
    return <p className="text-odin-muted text-sm">No active voice sessions.</p>;
  }
  return (
    <ul className="space-y-2 font-mono text-xs">
      {sessions.map((s) => (
        <li key={s.id} className="rounded border border-odin-border px-3 py-2 flex justify-between">
          <span>{s.id.slice(0, 8)}…</span>
          <span className="text-odin-muted">{s.state ?? "idle"}</span>
        </li>
      ))}
    </ul>
  );
}
