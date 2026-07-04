export function StatusPill({ status }: { status: string }) {
  return (
    <span className={`pill ${status}`}>
      <span className="dot" />
      {status}
    </span>
  );
}
