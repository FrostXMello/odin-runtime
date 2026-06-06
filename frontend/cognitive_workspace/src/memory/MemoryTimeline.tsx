export function MemoryTimeline({ events }: { events: string[] }) {
  return (
    <ol className="memory-timeline">
      {events.map((e, i) => (
        <li key={i}>{e}</li>
      ))}
    </ol>
  );
}
