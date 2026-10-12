export default function Loader({ label = "Loading…" }) {
  return <div className="loader-state" role="status"><span className="spinner" />{label}</div>;
}
