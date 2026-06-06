export function EvolutionDashboard({ sections }: { sections: string[] }) {
  return (
    <section className="evolution-dashboard">
      <h3>Self-development (approval required)</h3>
      <ul>
        {sections.map((s) => (
          <li key={s}>{s}</li>
        ))}
      </ul>
    </section>
  );
}
