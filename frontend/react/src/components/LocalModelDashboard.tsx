export function LocalModelDashboard({ status }: { status: Record<string, unknown> | null }) {
  if (!status) {
    return <p className="text-odin-muted text-sm">Loading local model runtime…</p>;
  }
  return (
    <dl className="grid grid-cols-2 gap-3 text-sm max-w-md">
      <dt className="text-odin-muted">Ollama</dt>
      <dd>{status.available ? "Available" : "Offline"}</dd>
      <dt className="text-odin-muted">Default model</dt>
      <dd className="font-mono">{String(status.default_model ?? "—")}</dd>
      <dt className="text-odin-muted">Loaded</dt>
      <dd>{((status.loaded_models as string[]) || []).join(", ") || "none"}</dd>
      <dt className="text-odin-muted">Queue</dt>
      <dd>{String(status.queue_size ?? 0)}</dd>
    </dl>
  );
}
