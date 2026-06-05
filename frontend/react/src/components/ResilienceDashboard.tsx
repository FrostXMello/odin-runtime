export function ResilienceDashboard({
  breakers,
}: {
  breakers: Array<{ name: string; state: string; failure_count: number }>;
}) {
  if (!breakers.length) {
    return <p className="text-odin-muted text-sm">All circuits closed — no failures recorded.</p>;
  }
  return (
    <ul className="space-y-2 text-sm font-mono max-w-lg">
      {breakers.map((b) => (
        <li key={b.name} className="flex justify-between border border-odin-border rounded px-3 py-2">
          <span>{b.name}</span>
          <span className={b.state === "open" ? "text-red-400" : "text-green-400"}>
            {b.state} ({b.failure_count})
          </span>
        </li>
      ))}
    </ul>
  );
}
