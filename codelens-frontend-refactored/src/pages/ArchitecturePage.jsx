import { useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import Button from "../components/common/Button";
import Loader from "../components/common/Loader";
import EmptyState from "../components/common/EmptyState";
import { getArchitectureSummary } from "../api/architectureApi";
import { useRepository } from "../context/RepositoryContext";
export default function ArchitecturePage() {
  const { activeRepository, goToImport } = useRepository(); const [result,setResult]=useState(null); const [busy,setBusy]=useState(false); const [error,setError]=useState("");
  async function analyze(){setBusy(true);setError("");try{setResult(await getArchitectureSummary());}catch(e){setError(e.message);}finally{setBusy(false);}}
  return <><PageHeader eyebrow="UNDERSTAND THE BIG PICTURE" title="Architecture" description="Generate a repository-grounded architecture analysis." action={<Button onClick={analyze} disabled={!activeRepository||busy}>✦ Analyze architecture</Button>}/>{!activeRepository ? <EmptyState title="No active repository" description="Import and activate a repository before analyzing its architecture." action={<Button onClick={goToImport}>Import repository</Button>}/> : <section className="card analysis-card"><div className="analysis-context"><strong>{activeRepository.repository}</strong><span>{activeRepository.repository_path}</span></div>{busy ? <Loader label="Analyzing architecture with CodeLens…"/> : error ? <div className="alert alert-error">{error}</div> : result ? <><h2>Architecture analysis</h2><div className="analysis-answer">{result.answer || result.response || JSON.stringify(result,null,2)}</div>{result.sources?.length>0&&<div className="sources"><strong>Referenced sources</strong>{result.sources.map((s,i)=><div className="source-item" key={i}>{typeof s==="string"?s:JSON.stringify(s)}</div>)}</div>}</> : <EmptyState icon="⌘" title="Ready to analyze" description="This uses your existing /api/chat RAG endpoint to request an architecture summary from the active repository." action={<Button onClick={analyze}>Analyze repository</Button>}/>}</section>}</>;
}
