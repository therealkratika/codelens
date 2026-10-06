"use client";

import { GitFork, Network, ListTree } from "lucide-react";
import { useArchitecture } from "@/hooks/useArchitecture";
import { FeatureFlowList } from "@/components/architecture/FeatureFlowList";
import { FeatureFlowDetail } from "@/components/architecture/FeatureFlowDetail";
import { DependencyGraph } from "@/components/architecture/DependencyGraph";
import { RoutesCatalog } from "@/components/architecture/RoutesCatalog";
import { Spinner } from "@/components/common/Spinner";
import type { FeatureFlow } from "@/types/architecture";

interface ArchitectureViewProps {
  onAskAboutFlow: (flow: FeatureFlow) => void;
  onOpenFile: (file: string, line?: number) => void;
}

export function ArchitectureView({
  onAskAboutFlow,
  onOpenFile,
}: ArchitectureViewProps) {
  const {
    flows,
    allFlows,
    graph,
    activeTab,
    setActiveTab,
    selectedFlow,
    selectedFlowId,
    setSelectedFlowId,
    flowSearch,
    setFlowSearch,
    isLoading,
    error,
  } = useArchitecture();

  return (
    <section className="page-container architecture-view-wrapper">
      {/* View Header */}
      <div className="architecture-header">
        <div>
          <p className="eyebrow">Repository Architecture</p>
          <h1 className="view-title">System Flows &amp; Dependency Graph</h1>
          <p className="view-subtext">
            Traced end-to-end execution paths from frontend API calls down to backend routes, controllers, and models.
          </p>
        </div>

        {/* Tab Navigator */}
        <div className="architecture-tabs-nav" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "flows"}
            className={`arch-tab-btn ${activeTab === "flows" ? "is-active" : ""}`}
            onClick={() => setActiveTab("flows")}
          >
            <GitFork className="w-4 h-4" />
            <span>Feature Flows</span>
            <span className="tab-badge">{allFlows.length}</span>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "graph"}
            className={`arch-tab-btn ${activeTab === "graph" ? "is-active" : ""}`}
            onClick={() => setActiveTab("graph")}
          >
            <Network className="w-4 h-4" />
            <span>Code Graph</span>
            {graph && <span className="tab-badge">{graph.summary.nodes}</span>}
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "routes"}
            className={`arch-tab-btn ${activeTab === "routes" ? "is-active" : ""}`}
            onClick={() => setActiveTab("routes")}
          >
            <ListTree className="w-4 h-4" />
            <span>API Catalog</span>
            <span className="tab-badge">{allFlows.length}</span>
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="architecture-loading-state">
          <Spinner />
          <span>Tracing codebase routes, controllers, and dependencies...</span>
        </div>
      ) : error ? (
        <div className="error-message">
          <p>{error}</p>
        </div>
      ) : activeTab === "flows" ? (
        <div className="flows-split-view">
          <div className="flows-sidebar-column">
            <FeatureFlowList
              flows={flows}
              selectedFlowId={selectedFlowId}
              searchQuery={flowSearch}
              onSearchChange={setFlowSearch}
              onSelectFlow={setSelectedFlowId}
            />
          </div>

          <div className="flows-detail-column">
            <FeatureFlowDetail
              flow={selectedFlow}
              onAskAboutFlow={onAskAboutFlow}
              onOpenFile={onOpenFile}
            />
          </div>
        </div>
      ) : activeTab === "graph" ? (
        <DependencyGraph graph={graph} onOpenFile={onOpenFile} />
      ) : (
        <RoutesCatalog
          flows={allFlows}
          onAskAboutRoute={onAskAboutFlow}
          onOpenFile={onOpenFile}
        />
      )}
    </section>
  );
}
