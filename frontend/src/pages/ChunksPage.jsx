import { useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import Button from "../components/common/Button";
import Loader from "../components/common/Loader";
import EmptyState from "../components/common/EmptyState";
import StatCard from "../components/dashboard/StatCard";
import { explainChunkIndex } from "../api/chunksApi";
import { useRepository } from "../context/RepositoryContext";

export default function ChunksPage() {
  const { activeRepository, repositories, goToImport } = useRepository();
  const [details, setDetails] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const active = repositories.find(
    (repo) => repo.repository_path === activeRepository?.repository_path
  );

  async function inspect() {
    setBusy(true);
    setError("");
    try {
      setDetails(await explainChunkIndex());
    } catch (err) {
      setError(err.message || "Could not inspect the index.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="RETRIEVAL INDEX"
        title="Indexed chunks"
        description="Inspect indexing metadata and ask the RAG pipeline to explain its chunking and retrieval flow."
        action={
          <Button onClick={inspect} disabled={!activeRepository || busy}>
            Inspect index
          </Button>
        }
      />

      {!activeRepository ? (
        <EmptyState
          title="No active repository"
          description="Import and activate a repository to inspect its indexing metadata."
          action={<Button onClick={goToImport}>Import repository</Button>}
        />
      ) : (
        <>
          <div className="stats-grid three-stats">
            <StatCard
              icon="▤"
              label="Repository"
              value={activeRepository.repository || "Active repository"}
              detail="Active index context"
            />
            <StatCard
              icon="⌘"
              label="Files indexed"
              value={active?.files ?? "—"}
              detail="Saved metadata"
              tone="blue"
            />
            <StatCard
              icon="▦"
              label="Code chunks"
              value={active?.chunks ?? "—"}
              detail="Saved metadata"
              tone="orange"
            />
          </div>

          <section className="card analysis-card">
            {busy ? (
              <Loader label="Inspecting index through CodeLens…" />
            ) : error ? (
              <div className="alert alert-error" role="alert">
                {error}
              </div>
            ) : details ? (
              <>
                <h2>Index and retrieval explanation</h2>
                <div className="analysis-answer">
                  {details.answer ||
                    details.response ||
                    JSON.stringify(details, null, 2)}
                </div>

                {details.sources?.length > 0 && (
                  <div className="sources">
                    <strong>Referenced sources</strong>
                    {details.sources.map((source, index) => (
                      <div className="source-item" key={index}>
                        {typeof source === "string"
                          ? source
                          : JSON.stringify(source)}
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <EmptyState
                icon="▦"
                title="Index metadata loaded"
                description="Aggregate file and chunk counts come from repository metadata. Inspect index asks the existing RAG endpoint to explain the indexing implementation."
              />
            )}
          </section>

          <p className="muted page-note">
            Individual chunk records are not available through the currently
            confirmed backend API, so this page does not fabricate chunk previews.
          </p>
        </>
      )}
    </>
  );
}