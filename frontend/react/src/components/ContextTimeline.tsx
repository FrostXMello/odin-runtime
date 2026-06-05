export function ContextTimeline({
  entries,
}: {
  entries: Array<{ timestamp?: string; message: string; source?: string }>;
}) {
  if (!entries.length) {
    return <p className="text-odin-muted text-sm">Enable context awareness to see timeline.</p>;
  }
  return (
    <ul className="space-y-2 text-sm max-h-[480px] overflow-y-auto">
      {entries.map((e, i) => (
        <li key={i} className="border-l-2 border-odin-accent/40 pl-3 py-1">
          <span className="text-xs text-odin-muted">{e.source ?? "context"}</span>
          <p>{e.message}</p>
        </li>
      ))}
    </ul>
  );
}
