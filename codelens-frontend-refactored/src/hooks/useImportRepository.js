import { useState } from "react";
import { importRepository, getImportStatus } from "../api/repositoryApi";
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
export default function useImportRepository({ onSuccess }) {
  const [busy, setBusy] = useState(false); const [message, setMessage] = useState(""); const [error, setError] = useState("");
  async function start(url) {
    setBusy(true); setError(""); setMessage("Starting repository import…");
    try {
      const job = await importRepository(url);
      if (!job.job_id) throw new Error("The backend did not return an import job ID.");
      for (let i=0; i<900; i++) {
        await sleep(1800);
        const result = await getImportStatus(job.job_id);
        const status = String(result.status || "").toLowerCase();
        if (["completed","success","succeeded","done"].includes(status)) {
          setMessage("Repository imported and indexed successfully."); await onSuccess?.(result); return result;
        }
        if (["failed","error"].includes(status)) throw new Error(result.error || "Repository import failed.");
        setMessage(result.message || (["running","processing","in_progress"].includes(status) ? "Cloning files and building the code index…" : `Import status: ${status || "waiting"}`));
      }
      throw new Error("Import is taking longer than expected. Refresh the repository list and check backend logs.");
    } catch (e) { setError(e.message || "Repository import failed."); setMessage(""); throw e; }
    finally { setBusy(false); }
  }
  return { start, busy, message, error, setError };
}
