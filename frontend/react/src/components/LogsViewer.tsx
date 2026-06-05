export function LogsViewer({ logs }: { logs: Array<Record<string, unknown>> }) {
  if (!logs.length) {
    return <p className="text-odin-muted text-sm">No audit logs.</p>;
  }

  return (
    <div className="font-mono text-xs space-y-1 max-h-[480px] overflow-y-auto">
      {logs.map((log, i) => (
        <div key={i} className="rounded bg-odin-bg border border-odin-border px-2 py-1">
          <span className="text-odin-muted">{String(log.timestamp ?? "")}</span>
          <span className="text-odin-accent ml-2">{String(log.type ?? "")}</span>
          {log.tool != null && <span className="ml-2">{String(log.tool)}</span>}
          {log.allowed != null && (
            <span className={log.allowed ? "text-emerald-400 ml-2" : "text-red-400 ml-2"}>
              {log.allowed ? "allowed" : "denied"}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
