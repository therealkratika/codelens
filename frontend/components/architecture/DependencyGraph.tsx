"use client";

import { useState, useMemo } from "react";
import {
  ArrowDownRight,
  ArrowUpRight,
  Code2,
  ExternalLink,
  FileCode,
  FolderTree,
  Network,
  Search,
} from "lucide-react";
import type { CodeGraphData, GraphNode } from "@/types/architecture";

interface DependencyGraphProps {
  graph: CodeGraphData | null;
  onOpenFile: (file: string, line?: number) => void;
}

export function DependencyGraph({ graph, onOpenFile }: DependencyGraphProps) {
  const [filterQuery, setFilterQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const nodes = useMemo(() => graph?.nodes || [], [graph]);
  const edges = useMemo(() => graph?.edges || [], [graph]);

  // Set default selection
  const selectedNode: GraphNode | null = useMemo(() => {
    if (selectedNodeId) {
      return nodes.find((n) => n.id === selectedNodeId) || nodes[0] || null;
    }
    return nodes[0] || null;
  }, [nodes, selectedNodeId]);

  // Filter nodes by category and search
  const filteredNodes = useMemo(() => {
    return nodes.filter((node) => {
      const matchesSearch =
        !filterQuery.trim() ||
        node.file.toLowerCase().includes(filterQuery.toLowerCase());

      if (!matchesSearch) return false;

      if (activeCategory === "all") return true;
      if (activeCategory === "frontend") return node.file.startsWith("frontend");
      if (activeCategory === "routes")
        return node.file.includes("route") || node.file.includes("routes");
      if (activeCategory === "controllers")
        return node.file.includes("controller");
      if (activeCategory === "models") return node.file.includes("model");

      return true;
    });
  }, [nodes, filterQuery, activeCategory]);

  // Calculate dependencies for selected node
  const outgoingEdges = useMemo(() => {
    if (!selectedNode) return [];
    return edges.filter((e) => e.source === selectedNode.file);
  }, [edges, selectedNode]);

  const incomingEdges = useMemo(() => {
    if (!selectedNode) return [];
    return edges.filter((e) => e.target === selectedNode.file);
  }, [edges, selectedNode]);

  if (!graph || nodes.length === 0) {
    return (
      <div className="graph-empty-state">
        <Network className="w-12 h-12 text-muted mb-3" />
        <h3>Code Graph Initializing</h3>
        <p>Analyzing import statements and function invocations across codebase...</p>
      </div>
    );
  }

  return (
    <div className="graph-workspace">
      {/* Top Controls */}
      <div className="graph-toolbar">
        <div className="graph-categories">
          {[
            { id: "all", label: "All Modules" },
            { id: "frontend", label: "Frontend" },
            { id: "routes", label: "Routes" },
            { id: "controllers", label: "Controllers" },
            { id: "models", label: "Models" },
          ].map((cat) => (
            <button
              key={cat.id}
              type="button"
              className={`cat-btn ${activeCategory === cat.id ? "is-active" : ""}`}
              onClick={() => setActiveCategory(cat.id)}
            >
              {cat.label}
            </button>
          ))}
        </div>

        <div className="graph-search">
          <Search className="w-4 h-4 search-icon" />
          <input
            type="text"
            className="graph-search-input"
            placeholder="Search module or file..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
          />
        </div>

        <div className="graph-stats-chip">
          <span>{graph.summary.nodes} Nodes</span>
          <span className="dot-sep">&bull;</span>
          <span>{graph.summary.edges} Edges</span>
        </div>
      </div>

      <div className="graph-layout">
        {/* Nodes Grid / Directory List */}
        <div className="graph-nodes-pane">
          <div className="pane-header">
            <h4>Code Modules ({filteredNodes.length})</h4>
          </div>

          <div className="node-cards-list">
            {filteredNodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              const fileName = node.file.split("/").pop() || node.file;
              const dirName = node.file.split("/").slice(0, -1).join("/");

              return (
                <button
                  key={node.id}
                  type="button"
                  className={`node-card ${isSelected ? "is-selected" : ""}`}
                  onClick={() => setSelectedNodeId(node.id)}
                >
                  <div className="node-card-top">
                    <FileCode className="w-4 h-4 text-accent" />
                    <span className="node-filename">{fileName}</span>
                  </div>
                  <span className="node-dir">{dirName || "root"}</span>

                  <div className="node-card-badges">
                    <span className="node-badge" title="Imported modules">
                      {node.imports_count} imports
                    </span>
                    <span className="node-badge" title="Functions declared">
                      {node.functions_count} fns
                    </span>
                    {node.calls_count > 0 && (
                      <span className="node-badge" title="Function calls">
                        {node.calls_count} calls
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Node Details & Connected Edges */}
        <div className="graph-inspector-pane">
          {selectedNode ? (
            <div className="node-inspector">
              <div className="inspector-header">
                <div className="inspector-title-row">
                  <FileCode className="w-5 h-5 text-accent" />
                  <div>
                    <h3 className="inspector-title">
                      {selectedNode.file.split("/").pop()}
                    </h3>
                    <code className="inspector-path">{selectedNode.file}</code>
                  </div>
                </div>

                <button
                  type="button"
                  className="btn-action-secondary"
                  onClick={() => onOpenFile(selectedNode.file)}
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>Open in Files</span>
                </button>
              </div>

              {/* Node Relationships: Inbound & Outbound */}
              <div className="inspector-grid">
                {/* Outgoing Imports */}
                <div className="inspector-section">
                  <div className="section-title-row">
                    <ArrowUpRight className="w-4 h-4 text-emerald-500" />
                    <h4>Imports / Dependencies ({outgoingEdges.length})</h4>
                  </div>
                  {outgoingEdges.length === 0 ? (
                    <p className="empty-hint">No outgoing import edges registered.</p>
                  ) : (
                    <div className="edge-list">
                      {outgoingEdges.map((edge, idx) => (
                        <div
                          key={`out-${edge.target}-${idx}`}
                          className="edge-item cursor-pointer"
                          onClick={() => {
                            const targetNode = nodes.find(
                              (n) => n.file === edge.target,
                            );
                            if (targetNode) setSelectedNodeId(targetNode.id);
                          }}
                        >
                          <span className="edge-relation">{edge.relation}</span>
                          <span className="edge-target-name">
                            {edge.target.split("/").pop()}
                          </span>
                          <code className="edge-target-path">{edge.target}</code>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Incoming Callers */}
                <div className="inspector-section">
                  <div className="section-title-row">
                    <ArrowDownRight className="w-4 h-4 text-emerald-500" />
                    <h4>Imported By / Callers ({incomingEdges.length})</h4>
                  </div>
                  {incomingEdges.length === 0 ? (
                    <p className="empty-hint">No inbound callers detected in index.</p>
                  ) : (
                    <div className="edge-list">
                      {incomingEdges.map((edge, idx) => (
                        <div
                          key={`in-${edge.source}-${idx}`}
                          className="edge-item cursor-pointer"
                          onClick={() => {
                            const sourceNode = nodes.find(
                              (n) => n.file === edge.source,
                            );
                            if (sourceNode) setSelectedNodeId(sourceNode.id);
                          }}
                        >
                          <span className="edge-relation">{edge.relation}</span>
                          <span className="edge-target-name">
                            {edge.source.split("/").pop()}
                          </span>
                          <code className="edge-target-path">{edge.source}</code>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Declared Functions */}
              <div className="inspector-section mt-4">
                <div className="section-title-row">
                  <Code2 className="w-4 h-4 text-stone-400" />
                  <h4>Exported Functions ({selectedNode.functions.length})</h4>
                </div>
                {selectedNode.functions.length === 0 ? (
                  <p className="empty-hint">No top-level function declarations parsed.</p>
                ) : (
                  <div className="functions-table">
                    {selectedNode.functions.map((fn, idx) => (
                      <div
                        key={`${fn.name}-${idx}`}
                        className="fn-row cursor-pointer"
                        onClick={() => onOpenFile(selectedNode.file, fn.start_line)}
                      >
                        <code className="fn-name">{fn.name}()</code>
                        <span className="fn-lines">
                          Lines {fn.start_line} &ndash; {fn.end_line}
                        </span>
                        <ExternalLink className="w-3 h-3 text-muted" />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="inspector-empty">
              <FolderTree className="w-10 h-10 text-muted opacity-40 mb-2" />
              <p>Select any code module to inspect its dependency connections.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
