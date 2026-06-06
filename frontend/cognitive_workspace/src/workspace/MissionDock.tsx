export function MissionDock({ missions }: { missions: string[] }) {
  return (
    <aside className="mission-dock">
      {missions.map((m) => (
        <div key={m} className="mission-chip">{m}</div>
      ))}
    </aside>
  );
}
