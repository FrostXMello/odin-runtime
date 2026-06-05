export function ReflectionReports({ report }: { report: Record<string, unknown> | null }) {
  if (!report) {
    return <p className="text-odin-muted text-sm">Run a workflow to generate reflection.</p>;
  }
  const findings = (report.findings as string[]) || [];
  const recs = (report.recommendations as string[]) || [];
  return (
    <div className="space-y-4 text-sm max-w-xl">
      <p>Success: {String(report.success)}</p>
      <div>
        <h4 className="text-odin-muted text-xs uppercase mb-2">Findings</h4>
        <ul className="list-disc pl-5 space-y-1">
          {findings.map((f, i) => (
            <li key={i}>{f}</li>
          ))}
        </ul>
      </div>
      <div>
        <h4 className="text-odin-muted text-xs uppercase mb-2">Recommendations</h4>
        <ul className="list-disc pl-5 space-y-1">
          {recs.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
