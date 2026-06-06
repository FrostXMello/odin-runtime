export function PatchProposals({ proposals }: { proposals: string[] }) {
  return (
    <ul className="patch-proposals">
      {proposals.map((p) => (
        <li key={p}>{p} — approval required</li>
      ))}
    </ul>
  );
}

export function CouncilView({ roles }: { roles: string[] }) {
  return (
    <div className="council-view">
      {roles.map((r) => (
        <span key={r} className="role-chip">{r}</span>
      ))}
    </div>
  );
}

export function RegressionHeatmap({ cells }: { cells: number[] }) {
  return (
    <div className="regression-heatmap">
      {cells.map((c, i) => (
        <div key={i} style={{ opacity: c / 100 }} className="cell" />
      ))}
    </div>
  );
}

export function StageTracker({ stage }: { stage: string }) {
  return <div className="stage-tracker">Stage: {stage}</div>;
}

export function ResumeCenter({ summary }: { summary: string }) {
  return <aside className="resume-center">{summary || "Ready to resume project"}</aside>;
}
