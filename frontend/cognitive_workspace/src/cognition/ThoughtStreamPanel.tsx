export function ThoughtStreamPanel({ lines }: { lines: string[] }) {
  return (
    <ul className="thought-stream">
      {lines.map((l, i) => (
        <li key={i}>{l}</li>
      ))}
    </ul>
  );
}
