export default function StatCard({ icon, label, value, detail, tone = "purple" }) {
  return <div className="stat-card"><div className={`stat-icon ${tone}`}>{icon}</div><div className="stat-content"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div></div>;
}
