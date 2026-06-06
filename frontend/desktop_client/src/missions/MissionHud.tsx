export function MissionHud({ missions }: { missions: string[] }) {
  return (
    <div className="mission-hud">
      {missions.map((m) => (
        <div key={m} className="mission-chip">
          {m}
        </div>
      ))}
    </div>
  );
}
