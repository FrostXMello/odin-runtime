export function ThoughtStream({ lines }: { lines: string[] }) {
  return (
    <ul className="thought-stream">
      {lines.map((line, i) => (
        <li key={i}>{line}</li>
      ))}
    </ul>
  );
}
