type Panel = { id: string; title: string; content: string };

export function WorkspaceGrid({ panels }: { panels: Panel[] }) {
  return (
    <section className="workspace-grid">
      {panels.map((p) => (
        <article key={p.id} className="panel">
          <h3>{p.title}</h3>
          <p>{p.content}</p>
        </article>
      ))}
    </section>
  );
}
