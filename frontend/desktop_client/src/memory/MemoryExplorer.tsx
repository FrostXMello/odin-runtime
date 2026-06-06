export function MemoryExplorer({ threads }: { threads: string[] }) {
  return (
    <ul className="memory-explorer">
      {threads.map((t) => (
        <li key={t}>{t}</li>
      ))}
    </ul>
  );
}
