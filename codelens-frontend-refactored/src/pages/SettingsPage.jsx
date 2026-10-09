import PageHeader from "../components/layout/PageHeader";
import { useRepository } from "../context/RepositoryContext";
export default function SettingsPage() {
  const { health, activeRepository } = useRepository();
  return <><PageHeader eyebrow="WORKSPACE" title="Settings" description="Frontend API configuration and current connection state."/><section className="card settings-card"><div className="setting-row"><div><strong>API endpoint</strong><p className="muted">Configured with Vite environment variables.</p></div><code>{import.meta.env.VITE_API_URL || "http://localhost:8000"}</code></div><div className="setting-row"><div><strong>Backend status</strong><p className="muted">FastAPI connectivity check.</p></div><span className={`status-pill ${health==="online"?"success":"neutral"}`}>{health}</span></div><div className="setting-row"><div><strong>Active repository</strong><p className="muted">Repository selected in this backend session.</p></div><strong>{activeRepository?.repository || "None"}</strong></div></section></>;
}
