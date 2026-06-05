export function ConversationTimeline({
  messages,
}: {
  messages: Array<{ role: string; content: string; timestamp?: string }>;
}) {
  return (
    <div className="space-y-3 max-h-[520px] overflow-y-auto">
      {messages.map((m, i) => (
        <div
          key={i}
          className={`rounded-lg px-3 py-2 text-sm max-w-[85%] ${
            m.role === "user"
              ? "ml-auto bg-odin-accent/20 text-odin-accent"
              : "bg-odin-panel border border-odin-border"
          }`}
        >
          <p className="text-xs text-odin-muted mb-1">{m.role}</p>
          {m.content}
        </div>
      ))}
    </div>
  );
}
