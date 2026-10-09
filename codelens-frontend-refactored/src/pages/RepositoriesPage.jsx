import PageHeader from "../components/layout/PageHeader";
import RepositoryCard from "../components/repository/RepositoryCard";
import EmptyState from "../components/common/EmptyState";
import Loader from "../components/common/Loader";
import Button from "../components/common/Button";
import { useRepository } from "../context/RepositoryContext";
import { useNavigate } from "react-router-dom";
export default function RepositoriesPage() {
  const { repositories, activeRepository, loading, activate, goToImport } = useRepository(); const navigate = useNavigate();
  async function choose(path) { await activate(path); navigate("/dashboard"); }
  return <><PageHeader eyebrow="REPOSITORY LIBRARY" title="Repositories" description="Manage and switch between saved codebases." action={<Button onClick={goToImport}>＋ Import repository</Button>}/>{loading ? <Loader label="Loading saved repositories…"/> : repositories.length ? <div className="repo-grid">{repositories.map(repo=><RepositoryCard key={repo.normalized_url||repo.repo_url||repo.repository_path} repo={repo} active={activeRepository?.repository_path===repo.repository_path} onActivate={choose}/>)}</div> : <EmptyState icon="▤" title="No saved repositories" description="Import a GitHub repository to get started." action={<Button onClick={goToImport}>Import repository</Button>}/>}</>;
}
