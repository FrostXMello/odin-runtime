export function AttentionHeatmap({ cells }: { cells: number[] }) {
  return (
    <div className="attention-heatmap">
      {cells.map((c, i) => (
        <div key={i} style={{ opacity: c / 100 }} className="cell" />
      ))}
    </div>
  );
}
