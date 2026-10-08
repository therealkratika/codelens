import { apiClient } from "@/lib/api/client";
import type {
  ArchitectureFlowsResponse,
  CodeGraphData,
  FeatureFlow,
} from "@/types/architecture";

export async function getFeatureFlows(): Promise<FeatureFlow[]> {
  const data = await apiClient.get<ArchitectureFlowsResponse>(
    "/architecture/flows",
    20_000,
  );
  return data.flows;
}

export async function getCodeGraph(): Promise<CodeGraphData> {
  return apiClient.get<CodeGraphData>("/architecture/graph", 20_000);
}
