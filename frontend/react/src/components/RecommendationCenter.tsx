export function RecommendationCenter({
  items,
  onDismiss,
}: {
  items: Array<{
    id: string;
    title: string;
    message: string;
    category: string;
    explainable?: Record<string, unknown>;
  }>;
  onDismiss?: (id: string) => void;
}) {
  if (!items.length) {
    return <p className="text-odin-muted text-sm">No proactive recommendations.</p>;
  }
  return (
    <ul className="space-y-3 max-w-xl">
      {items.map((r) => (
        <li key={r.id} className="rounded-lg border border-odin-border bg-odin-panel p-4">
          <div className="flex justify-between items-start gap-2">
            <div>
              <span className="text-xs text-odin-accent uppercase">{r.category}</span>
              <h4 className="font-medium mt-1">{r.title}</h4>
              <p className="text-sm text-odin-muted mt-1">{r.message}</p>
            </div>
            {onDismiss && (
              <button
                onClick={() => onDismiss(r.id)}
                className="text-xs text-odin-muted hover:text-slate-200"
              >
                Dismiss
              </button>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
