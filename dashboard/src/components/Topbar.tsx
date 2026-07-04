export function Topbar({ title }: { title: string }) {
  return (
    <header className="topbar">
      <span className="topbar-title">{title}</span>
      <div className="topbar-right">
        <span className="backend-pill">
          <span className="dot" />
          Ollama · local
        </span>
        <span className="health">
          <span className="dot lg" />
          All systems operational
        </span>
      </div>
    </header>
  );
}
