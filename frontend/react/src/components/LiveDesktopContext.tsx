export function LiveDesktopContext({ state }: { state: Record<string, unknown> | null }) {
  if (!state) return <p className="text-odin-muted text-sm">Loading desktop runtime…</p>;
  const explain = (state.explainable as Record<string, unknown>) || {};
  return (
    <dl className="grid gap-2 text-sm max-w-lg">
      <div className="flex justify-between">
        <dt className="text-odin-muted">Collector</dt>
        <dd>{state.enabled ? "Active (opt-in)" : "Disabled"}</dd>
      </div>
      <div className="flex justify-between">
        <dt className="text-odin-muted">Sources</dt>
        <dd>{String((explain.collectors_active as string[])?.join(", ") ?? "—")}</dd>
      </div>
      <div className="flex justify-between">
        <dt className="text-odin-muted">Events</dt>
        <dd>{String(explain.event_count ?? 0)}</dd>
      </div>
    </dl>
  );
}
