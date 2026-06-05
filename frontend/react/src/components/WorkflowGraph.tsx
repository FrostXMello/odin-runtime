import { WorkflowRun } from "@/lib/api";

export function WorkflowGraph({ workflow }: { workflow: WorkflowRun | null }) {
  if (!workflow) {
    return <p className="text-odin-muted text-sm">Select a workflow run to view steps.</p>;
  }
  const steps = Object.entries(workflow.step_results || {});
  return (
    <div className="space-y-3">
      <p className="text-sm font-medium">{workflow.objective}</p>
      <p className="text-xs text-odin-muted">Status: {workflow.status}</p>
      <div className="flex flex-col gap-2">
        {steps.length === 0 && <p className="text-xs text-odin-muted">No step results yet.</p>}
        {steps.map(([id, result]) => {
          const r = result as Record<string, unknown>;
          return (
            <div
              key={id}
              className={`rounded border px-3 py-2 text-xs font-mono ${
                r.success ? "border-emerald-500/30" : "border-red-500/30"
              }`}
            >
              Step {id} — {r.success ? "completed" : "failed"}
            </div>
          );
        })}
      </div>
    </div>
  );
}
