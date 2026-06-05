import { Task } from "@/lib/api";

const STATUS_COLORS: Record<string, string> = {
  pending: "text-slate-400",
  queued: "text-blue-400",
  assigned: "text-blue-300",
  running: "text-amber-400",
  completed: "text-emerald-400",
  failed: "text-red-400",
  cancelled: "text-odin-muted",
};

export function TaskQueueViewer({ tasks }: { tasks: Task[] }) {
  if (!tasks.length) {
    return <p className="text-odin-muted text-sm">No tasks in queue.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-odin-muted border-b border-odin-border">
            <th className="py-2 pr-4">Title</th>
            <th className="py-2 pr-4">Status</th>
            <th className="py-2 pr-4">Agent</th>
            <th className="py-2">ID</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr key={t.id} className="border-b border-odin-border/50">
              <td className="py-2 pr-4">{t.title}</td>
              <td className={`py-2 pr-4 font-mono text-xs ${STATUS_COLORS[t.status] ?? ""}`}>
                {t.status}
              </td>
              <td className="py-2 pr-4 font-mono text-xs text-odin-accent">
                {t.assigned_agent ?? "—"}
              </td>
              <td className="py-2 font-mono text-xs text-odin-muted">{t.id.slice(0, 8)}…</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
