type Panel = { id: string; title: string };

export function DraggablePanels({ panels }: { panels: Panel[] }) {
  return (
    <div className="panel-grid">
      {panels.map((p) => (
        <section key={p.id} className="panel" draggable>
          <h3>{p.title}</h3>
        </section>
      ))}
    </div>
  );
}
