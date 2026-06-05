export function TrustSecurityCenter({ dashboard }: { dashboard: Record<string, unknown> | null }) {
  if (!dashboard) return <p className="text-odin-muted text-sm">Loading trust system…</p>;
  const anomalies = (dashboard.recent_anomalies as Array<Record<string, unknown>>) || [];
  return (
    <div className="space-y-4 max-w-xl text-sm">
      <p className="text-odin-muted">
        Sensitive workflows tracked: {String(dashboard.sensitive_workflows ?? 0)}
      </p>
      {anomalies.length > 0 && (
        <ul className="space-y-1">
          {anomalies.map((a, i) => (
            <li key={i} className="text-red-300/80">
              {String(a.detail)}
            </li>
          ))}
        </ul>
      )}
      {!anomalies.length && <p className="text-odin-muted">No recent security anomalies.</p>}
    </div>
  );
}
