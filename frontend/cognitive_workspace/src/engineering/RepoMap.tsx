export function RepoMap({ files }: { files: string[] }) {
  return (
    <div className="repo-map">
      {files.map((f) => (
        <div key={f} className="repo-node">{f}</div>
      ))}
    </div>
  );
}

export function FileGraph({ edges }: { edges: string[] }) {
  return (
    <svg className="file-graph" viewBox="0 0 320 120">
      {edges.map((e, i) => (
        <line key={e} x1={10 + i * 40} y1="20" x2={50 + i * 40} y2="90" stroke="#38bdf8" />
      ))}
    </svg>
  );
}
