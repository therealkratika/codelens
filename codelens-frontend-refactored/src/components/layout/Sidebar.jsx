import { NavLink } from "react-router-dom";
const groups = [
  { label: "WORKSPACE", links: [{ to: "/dashboard", icon: "◫", label: "Dashboard" }, { to: "/repositories", icon: "▤", label: "Repositories" }] },
  { label: "EXPLORE CODE", links: [{ to: "/architecture", icon: "⌘", label: "Architecture" }, { to: "/code", icon: "</>", label: "Code explorer" }, { to: "/chunks", icon: "▦", label: "Indexed chunks" }, { to: "/chat", icon: "✳", label: "Code chat", tag: "AI" }] },
];
export default function Sidebar({ onImport, health }) {
  return <aside className="sidebar">
    <NavLink to="/dashboard" className="brand"><span className="brand-mark">⌘</span><span><strong>CodeLens</strong><small>AI code companion</small></span></NavLink>
    {groups.map(group => <section className="nav-section" key={group.label}><div className="nav-label">{group.label}</div>{group.links.map(link => <NavLink key={link.to} to={link.to} className={({isActive}) => `nav-item ${isActive ? "active" : ""}`}><span className="nav-icon">{link.icon}</span><span>{link.label}</span>{link.tag && <span className="nav-new">{link.tag}</span>}</NavLink>)}</section>)}
    <section className="nav-section"><div className="nav-label">PREFERENCES</div><NavLink to="/settings" className={({isActive}) => `nav-item ${isActive ? "active" : ""}`}><span className="nav-icon">⚙</span><span>Settings</span></NavLink></section>
    <div className="sidebar-spacer" />
    <div className="sidebar-tip"><div className="tip-icon">✦</div><strong>Switch codebases anytime</strong><p>Import another repository to refresh your workspace context.</p><button onClick={onImport}>Import repository ↗</button></div>
    <div className="profile-row"><div className="profile-avatar">CL</div><div className="profile-copy"><strong>Developer workspace</strong><small>Backend: {health}</small></div><span className={`connection-dot ${health}`} /></div>
  </aside>;
}
