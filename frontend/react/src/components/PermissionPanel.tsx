import { PermissionRequest } from "@/lib/api";
import { api } from "@/lib/api";

interface Props {
  requests: PermissionRequest[];
  onApproved: () => void;
}

export function PermissionPanel({ requests, onApproved }: Props) {
  if (!requests.length) {
    return <p className="text-odin-muted text-sm">No pending permission requests.</p>;
  }

  return (
    <div className="space-y-3">
      {requests.map((r) => (
        <div key={r.id} className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-4">
          <p className="font-mono text-sm text-amber-200">{r.tool_name}</p>
          <p className="text-xs text-odin-muted mt-1">{r.reason}</p>
          <p className="text-xs text-odin-muted">Agent: {r.agent_id}</p>
          <button
            onClick={async () => {
              await api.permissions.approve(r.id);
              onApproved();
            }}
            className="mt-3 px-3 py-1.5 text-xs rounded bg-amber-500/20 text-amber-200 hover:bg-amber-500/30"
          >
            Approve
          </button>
        </div>
      ))}
    </div>
  );
}
