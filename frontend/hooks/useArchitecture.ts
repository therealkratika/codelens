"use client";

import { useEffect, useState, useMemo } from "react";
import { getFeatureFlows, getCodeGraph } from "@/lib/api/architecture";
import type { FeatureFlow, CodeGraphData } from "@/types/architecture";

export type ArchitectureTab = "flows" | "graph" | "routes";

export function useArchitecture() {
  const [flows, setFlows] = useState<FeatureFlow[]>([]);
  const [graph, setGraph] = useState<CodeGraphData | null>(null);
  const [activeTab, setActiveTab] = useState<ArchitectureTab>("flows");
  const [selectedFlowId, setSelectedFlowId] = useState<string | null>(null);
  const [flowSearch, setFlowSearch] = useState("");
  const [selectedGraphNodeId, setSelectedGraphNodeId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setIsLoading(true);
      setError(null);
      try {
        const [flowsData, graphData] = await Promise.all([
          getFeatureFlows(),
          getCodeGraph(),
        ]);
        if (!cancelled) {
          setFlows(flowsData);
          setGraph(graphData);
          if (flowsData.length > 0) {
            setSelectedFlowId(flowsData[0].id);
          }
          if (graphData.nodes.length > 0) {
            setSelectedGraphNodeId(graphData.nodes[0].id);
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError("Failed to load codebase architecture analysis.");
          console.error(err);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadData();
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredFlows = useMemo(() => {
    if (!flowSearch.trim()) return flows;
    const query = flowSearch.toLowerCase();
    return flows.filter(
      (flow) =>
        flow.name.toLowerCase().includes(query) ||
        flow.route?.path.toLowerCase().includes(query) ||
        flow.controller?.controller_function.toLowerCase().includes(query) ||
        flow.frontend_api?.endpoint.toLowerCase().includes(query),
    );
  }, [flows, flowSearch]);

  const selectedFlow = useMemo(() => {
    return flows.find((f) => f.id === selectedFlowId) || flows[0] || null;
  }, [flows, selectedFlowId]);

  return {
    flows: filteredFlows,
    allFlows: flows,
    graph,
    activeTab,
    setActiveTab,
    selectedFlow,
    selectedFlowId,
    setSelectedFlowId,
    flowSearch,
    setFlowSearch,
    selectedGraphNodeId,
    setSelectedGraphNodeId,
    isLoading,
    error,
  };
}
