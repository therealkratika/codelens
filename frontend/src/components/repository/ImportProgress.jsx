export default function ImportProgress({ message, busy }) {
  if (!message && !busy) return null;
  return <div className="import-progress"><span className={busy ? "spinner" : "progress-check"}>{busy ? "" : "✓"}</span><div><strong>{busy ? "Preparing your codebase" : "Import status"}</strong><p>{message}</p></div></div>;
}
