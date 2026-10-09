export default function SourceReferences({ sources = [] }) {
  if (!sources.length) return null;
  return <div className="sources"><strong>Sources</strong>{sources.map((source, i) => <div className="source-item" key={i}>▧ {typeof source === "string" ? source : source.file_path || source.file || source.source || source.path || JSON.stringify(source)}</div>)}</div>;
}
