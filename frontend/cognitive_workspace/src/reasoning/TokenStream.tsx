export function TokenStream({ tokens }: { tokens: string[] }) {
  return (
    <div className="token-stream">
      {tokens.map((t, i) => (
        <span key={i} className="token">{t}</span>
      ))}
    </div>
  );
}
