import { useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import Button from "../components/common/Button";
import { useRepository } from "../context/RepositoryContext";
import { askCodebase } from "../api/chatApi";
import EmptyState from "../components/common/EmptyState";
export default function CodeExplorerPage() {
  const { activeRepository, goToImport } = useRepository(); const [query,setQuery]=useState(""); const [answer,setAnswer]=useState(null); const [busy,setBusy]=useState(false); const [error,setError]=useState("");
  async function search(e){e.preventDefault();if(!query.trim())return;setBusy(true);setError("");try{setAnswer(await askCodebase(`Find and explain the most relevant source files and implementation for this request: ${query.trim()}. Include file paths and cite sources where possible.`));}catch(err){setError(err.message);}finally{setBusy(false);}}
  return <><PageHeader eyebrow="SOURCE CONTEXT" title="Code explorer" description="Search code by describing the function or implementation you need."/><section className="card"><form className="explorer-search" onSubmit={search}><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="e.g. Where is JWT authentication implemented?" disabled={!activeRepository||busy}/><Button type="submit" disabled={!activeRepository||busy||!query.trim()}>{busy?"Searching…":"Search code"}</Button></form>{!activeRepository ? <EmptyState title="No active repository" description="Import and activate a repository to search its source context." action={<Button onClick={goToImport}>Import repository</Button>}/> : error ? <div className="alert alert-error">{error}</div> : answer && <div className="analysis-answer"><h3>Code context</h3>{answer.answer||answer.response||JSON.stringify(answer,null,2)}{answer.sources?.map((s,i)=><div className="source-item" key={i}>{typeof s==="string"?s:JSON.stringify(s)}</div>)}</div>}</section><p className="muted page-note">This page uses RAG chat retrieval; it does not yet expose a raw file tree or open-file viewer.</p></>;
}
