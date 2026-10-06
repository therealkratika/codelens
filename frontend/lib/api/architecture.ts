import { apiClient } from "@/lib/api/client";
import type {
  ArchitectureFlowsResponse,
  CodeGraphData,
  FeatureFlow,
} from "@/types/architecture";
import { FALLBACK_FLOWS, FALLBACK_GRAPH } from "@/lib/mock/fallbackData";

export async function getFeatureFlows(): Promise<FeatureFlow[]> {
  try {
    const data = await apiClient.get<ArchitectureFlowsResponse>(
      "/architecture/flows",
      20_000,
    );
    return data.flows && data.flows.length > 0 ? data.flows : FALLBACK_FLOWS;
  } catch (err) {
    console.warn("Using fallback flows data:", err);
    return FALLBACK_FLOWS;
  }
}

export async function getCodeGraph(): Promise<CodeGraphData> {
  try {
    const data = await apiClient.get<CodeGraphData>(
      "/architecture/graph",
      20_000,
    );
    return data && data.nodes && data.nodes.length > 0 ? data : FALLBACK_GRAPH;
  } catch (err) {
    console.warn("Using fallback code graph data:", err);
    return FALLBACK_GRAPH;
  }
}
