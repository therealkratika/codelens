import { useLocation, useNavigate } from "react-router-dom";
const labels = { "/dashboard": "Dashboard", "/repositories": "Repositories", "/architecture": "Architecture", "/code": "Code explorer", "/chunks": "Indexed chunks", "/chat": "Code chat", "/settings": "Settings" };
export default function Topbar({ health, activeRepository, onImport }) {
  const location = useLocation(); const navigate = useNavigate();
  return <header className="topbar"><div className="breadcrumb"><span>Workspace</span><span>/</span><strong>{labels[location.pathname] || "Dashboard"}</strong></div><div className="topbar-right"><span className={`api-status ${health}`}><i className="status-dot" />API {health}</span><span className="topbar-divider" /><div className="repo-indicator"><span className="repo-indicator-icon">⌘</span><span><small>ACTIVE REPOSITORY</small><strong>{activeRepository?.repository || "No repository selected"}</strong></span></div><button className="switch-repo" onClick={onImport}>Switch / import</button></div></header>;
}
