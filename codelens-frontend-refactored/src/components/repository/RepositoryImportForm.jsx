import { useState } from "react";
import Button from "../common/Button";
export default function RepositoryImportForm({ onSubmit, busy }) {
  const [url, setUrl] = useState(""); const [validation, setValidation] = useState("");
  function submit(e) {
    e.preventDefault(); const value = url.trim().replace(/\.git$/, "").replace(/\/$/, "");
    if (!/^https:\/\/github\.com\/[^/]+\/[^/]+$/i.test(value)) { setValidation("Enter a GitHub URL like https://github.com/owner/repository"); return; }
    setValidation(""); onSubmit(url.trim());
  }
  return <form className="import-form" onSubmit={submit}><label htmlFor="repo-url">GitHub repository URL</label><div className="input-with-icon"><span>↗</span><input id="repo-url" type="url" placeholder="https://github.com/owner/repository" value={url} onChange={e=>setUrl(e.target.value)} disabled={busy}/></div>{validation && <p className="field-error">{validation}</p>}<Button type="submit" className="full-width" disabled={busy || !url.trim()}>{busy ? <><span className="spinner"/> Importing and indexing…</> : <>Import repository <span>→</span></>}</Button></form>;
}
