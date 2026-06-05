import { OdinEvent } from "@/lib/api";

export function WatcherDashboard({ insights }: { insights: OdinEvent[] }) {
  if (!insights.length) {
    return <p className="text-odin-muted text-sm">No watcher insights yet (background loops).</p>;
  }
  return (
    <ul className="space-y-2 text-sm max-h-[480px] overflow-y-auto">
      {insights.map((e) => (
        <li key={e.id} className="rounded border border-odin-border bg-odin-panel p-3">
          <span className="text-xs font-mono text-odin-accent">{e.type}</span>
          <p className="mt-1 text-odin-muted">{JSON.stringify(e.payload).slice(0, 200)}</p>
        </li>
      ))}
    </ul>
  );
}
