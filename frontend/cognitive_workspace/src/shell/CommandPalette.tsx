export function CommandPalette({ onRun }: { onRun: (q: string) => void }) {
  return (
    <input
      className="command-palette"
      placeholder="Quick command…"
      onKeyDown={(e) => {
        if (e.key === "Enter") onRun((e.target as HTMLInputElement).value);
      }}
    />
  );
}
