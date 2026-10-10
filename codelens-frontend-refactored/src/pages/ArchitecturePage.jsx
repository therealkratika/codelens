import { useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import Button from "../components/common/Button";
import Loader from "../components/common/Loader";
import EmptyState from "../components/common/EmptyState";
import { getArchitectureFlows, getArchitectureGraph } from "../api/architectureApi";
import { useRepository } from "../context/RepositoryContext";

export default function ArchitecturePage() {
  const { activeRepository, goToImport } = useRepository();
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function analyze() {
    setBusy(true);
    setError("");
    try {
      const [flows, graph] = await Promise.all([
        getArchitectureFlows(),
        getArchitectureGraph(),
      ]);
      setResult({ flows, graph });
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="UNDERSTAND THE BIG PICTURE"
        title="Architecture"
        description="Explore repository dependencies and traced frontend-to-backend flows."
        action={
          <Button onClick={analyze} disabled={!activeRepository || busy}>
            ✦ Analyze architecture
          </Button>
        }
      />
      {!activeRepository ? (
        <EmptyState
          title="No active repository"
          description="Import and activate a repository before analyzing its architecture."
          action={<Button onClick={goToImport}>Import repository</Button>}
        />
      ) : (
        <section className="card analysis-card">
          <div className="analysis-context">
            <strong>{activeRepository.repository}</strong>
            <span>{activeRepository.repository_path}</span>
          </div>
          {busy ? (
            <Loader label="Analyzing architecture with CodeLens…" />
          ) : error ? (
            <div className="alert alert-error">{error}</div>
          ) : result ? (
            <>
              <div className="architecture-stats">
                <div className="architecture-stat">
                  <strong>{result.graph.summary?.nodes ?? result.graph.nodes?.length ?? 0}</strong>
                  <span>Code files</span>
                </div>
                <div className="architecture-stat">
                  <strong>{result.graph.summary?.edges ?? result.graph.edges?.length ?? 0}</strong>
                  <span>Relationships</span>
                </div>
                <div className="architecture-stat">
                  <strong>{result.flows.total ?? result.flows.flows?.length ?? 0}</strong>
                  <span>Traced flows</span>
                </div>
              </div>

              <div className="architecture-section">
                <h2>Frontend-to-backend flows</h2>
                {result.flows.flows?.length ? (
                  <div className="architecture-flow-list">
                    {result.flows.flows.map((flow, index) => {
                      const api = flow.frontend_api;
                      const route = flow.route;
                      const controller = flow.controller;
                      return (
                        <article
                          className="architecture-flow"
                          key={flow.id || `${flow.name || "flow"}-${index}`}
                        >
                          <strong>{flow.name || api?.function || "Unnamed flow"}</strong>
                          {api && (
                            <div className="architecture-flow-step">
                              <span>Frontend API</span>
                              <code>
                                {api.method ? `${api.method} ` : ""}
                                {api.resolved_endpoint || api.endpoint || api.file || "Endpoint unavailable"}
                              </code>
                            </div>
                          )}
                          {route ? (
                            <div className="architecture-flow-step">
                              <span>Backend route</span>
                              <code>
                                {route.method ? `${route.method} ` : ""}
                                {route.path || route.handler || "Route unavailable"}
                              </code>
                            </div>
                          ) : (
                            <p className="muted">No matching backend route was identified.</p>
                          )}
                          {controller && (
                            <div className="architecture-flow-step">
                              <span>Controller</span>
                              <code>
                                {controller.controller_file || controller.file || controller.name || "Resolved"}
                              </code>
                            </div>
                          )}
                        </article>
                      );
                    })}
                  </div>
                ) : (
                  <p className="muted">No frontend API flows were found for this repository.</p>
                )}
              </div>

              <div className="architecture-section">
                <h2>Code dependency map</h2>
                {result.graph.nodes?.length ? (
                  <div className="architecture-node-list">
                    {result.graph.nodes.map((node) => (
                      <div className="architecture-node" key={node.id || node.file}>
                        <strong>{node.file || node.id}</strong>
                        <span>
                          {node.functions_count ?? node.functions?.length ?? 0} functions
                          {" · "}
                          {node.imports_count ?? node.imports?.length ?? 0} imports
                          {" · "}
                          {node.calls_count ?? node.calls?.length ?? 0} calls
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="muted">No code graph nodes were returned.</p>
                )}
              </div>
            </>
          ) : (
            <EmptyState
              icon="⌘"
              title="Ready to analyze"
              description="Load the dependency graph and frontend-to-backend flows from the active repository."
              action={<Button onClick={analyze}>Analyze repository</Button>}
            />
          )}
        </section>
      )}
    </>
  );
}
