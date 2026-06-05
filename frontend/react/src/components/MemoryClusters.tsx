export function MemoryClusters({ clusters }: { clusters: Array<Record<string, unknown>> }) {
  return (
    <div className="grid gap-3 md:grid-cols-2">
      {clusters.map((c) => (
        <div key={String(c.project)} className="rounded-lg border border-odin-border bg-odin-panel p-4">
          <h3 className="font-mono text-odin-accent text-sm">{String(c.project)}</h3>
          <p className="text-xs text-odin-muted mt-2">
            {(c.keywords as string[])?.slice(0, 6).join(", ")}
          </p>
        </div>
      ))}
    </div>
  );
}
