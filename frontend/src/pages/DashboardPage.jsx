import { useNavigate } from "react-router-dom";
import PageHeader from "../components/layout/PageHeader";
import Button from "../components/common/Button";
import StatCard from "../components/dashboard/StatCard";
import FeatureCard from "../components/dashboard/FeatureCard";
import RepositoryCard from "../components/repository/RepositoryCard";
import EmptyState from "../components/common/EmptyState";
import { useRepository } from "../context/RepositoryContext";
import { formatCount } from "../utils/formatters";
export default function DashboardPage() {
  const { repositories, activeRepository, health, loading, goToImport, activate } = useRepository(); const navigate = useNavigate();
  const active = repositories.find(r => r.repository_path === activeRepository?.repository_path);
  return <><PageHeader eyebrow="YOUR WORKSPACE" title="Codebase dashboard" description="An overview of the repository you're exploring." action={<Button onClick={goToImport}>＋ Import repository</Button>}/>
    <section className="dashboard-hero"><div><span className="hero-chip">✦ REPOSITORY INTELLIGENCE</span><h2>{activeRepository?.repository || "Your codebase workspace"}</h2><p>{activeRepository ? "Explore architecture, indexed chunks, source context, or ask the AI assistant." : "Choose a repository to begin exploring its code and architecture."}</p><div className="hero-actions"><Button variant="light" onClick={()=>navigate("/chat")}>Ask CodeLens →</Button><Button variant="ghost" onClick={()=>navigate("/architecture")}>View architecture</Button></div></div><div className="dashboard-hero-symbol">⌘<span>✧</span></div></section>
    <div className="stats-grid"><StatCard icon="▤" label="Repositories" value={loading?"—":formatCount(repositories.length)} detail="Saved in workspace"/><StatCard icon="⌘" label="Files indexed" value={loading?"—":formatCount(active?.files)} detail="Current repository" tone="blue"/><StatCard icon="▦" label="Code chunks" value={loading?"—":formatCount(active?.chunks)} detail="Retrieval-ready segments" tone="orange"/><StatCard icon="◉" label="Backend" value={health==="online"?"Connected":health==="checking"?"Checking":"Offline"} detail="FastAPI connection" tone="green"/></div>
    <section className="explore-section"><div className="section-heading"><div><p className="eyebrow">EXPLORE YOUR CODE</p><h2>Workspace tools</h2></div></div><div className="tool-grid"><FeatureCard to="/architecture" icon="⌘" title="Architecture" description="Understand modules, dependencies, and data flow."/><FeatureCard to="/code" icon="</>" title="Code explorer" description="Explore code context and source-level questions."/><FeatureCard to="/chunks" icon="▦" title="Indexed chunks" description="Review chunk metadata and retrieval behavior."/><FeatureCard to="/chat" icon="✳" title="Code chat" description="Ask natural-language questions grounded in your codebase."/></div></section>
    <section className="recent-section"><div className="section-heading"><div><p className="eyebrow">LIBRARY</p><h2>Saved repositories</h2></div><button className="text-button" onClick={goToImport}>Import another →</button></div>{loading ? <div className="loading-box">Loading repositories…</div> : repositories.length ? <div className="repo-grid">{repositories.slice(0,3).map(repo=><RepositoryCard key={repo.normalized_url||repo.repo_url||repo.repository_path} repo={repo} active={activeRepository?.repository_path===repo.repository_path} onActivate={async path=>{await activate(path);}}/>)}</div> : <EmptyState icon="▤" title="No repositories found" description="Import a repository to start building your code intelligence workspace." action={<Button onClick={goToImport}>Import repository</Button>}/>}</section>
  </>;
}
