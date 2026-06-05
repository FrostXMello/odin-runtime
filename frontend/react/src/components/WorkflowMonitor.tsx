import { WorkflowRun } from "@/lib/api";

export function WorkflowMonitor({ workflows }: { workflows: WorkflowRun[] }) {
  if (!workflows.length) {
    return <p className="text-odin-muted text-sm">No workflow runs yet.</p>;
  }

  return (
    <div className="space-y-3">
      {[...workflows].reverse().map((w) => (
        <div key={w.id} className="rounded-lg border border-odin-border bg-odin-panel p-4">
          <div className="flex justify-between items-start gap-4">
            <p className="text-sm font-medium">{w.objective}</p>
            <span
              className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                w.status === "completed"
                  ? "bg-emerald-500/20 text-emerald-400"
                  : w.status === "failed"
                    ? "bg-red-500/20 text-red-400"
                    : "bg-amber-500/20 text-amber-400"
              }`}
            >
              {w.status}
            </span>
          </div>
          <p className="text-xs text-odin-muted mt-2 font-mono">{w.id.slice(0, 8)}…</p>
          {w.error && <p className="text-xs text-red-400 mt-2">{w.error}</p>}
          <p className="text-xs text-odin-muted mt-1">
            Steps completed: {Object.keys(w.step_results || {}).length}
          </p>
        </div>
      ))}
    </div>
  );
}
