export function RuntimeHealth({
  status,
  agents,
}: {
  status: Record<string, unknown> | null;
  agents: Array<Record<string, unknown>>;
}) {
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-odin-border bg-odin-panel p-4">
        <p className="text-sm text-odin-muted">Supervisor</p>
        <p className="text-lg font-mono text-odin-accent mt-1">
          {status?.running ? "running" : "stopped"}
        </p>
        <p className="text-xs text-odin-muted mt-2">
          Services: {(status?.services as string[])?.join(", ") || "—"}
        </p>
      </div>
      <div className="grid gap-2">
        {agents.map((a) => (
          <div key={String(a.agent_id)} className="rounded border border-odin-border px-3 py-2 text-sm flex justify-between">
            <span className="font-mono text-odin-accent">{String(a.agent_id)}</span>
            <span className="text-odin-muted">{String(a.health)} · {String(a.state)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
