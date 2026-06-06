export function IssueTimeline({ issues }: { issues: string[] }) {
  return (
    <ol className="issue-timeline">
      {issues.map((i) => (
        <li key={i}>{i}</li>
      ))}
    </ol>
  );
}

export function DebugWatchtower({ errors }: { errors: string[] }) {
  return (
    <section className="debug-watchtower">
      <h4>Debug Watchtower</h4>
      {errors.map((e) => (
        <div key={e} className="error-chip">{e}</div>
      ))}
    </section>
  );
}
