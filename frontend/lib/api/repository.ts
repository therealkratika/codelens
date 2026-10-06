import { apiClient } from "@/lib/api/client";
import type {
  RepositoryDetails,
  RepositoryImportRequest,
  RepositoryImportResponse,
  RepositoryStatus,
} from "@/types/repository";

export function importRepository(
  repoUrl: string,
): Promise<RepositoryImportResponse> {
  const request: RepositoryImportRequest = { repo_url: repoUrl };
  return apiClient.post<RepositoryImportResponse, RepositoryImportRequest>(
    "/repository/import",
    request,
    600_000,
  );
}

export function getRepositoryStatus(): Promise<RepositoryStatus> {
  return apiClient.get<RepositoryStatus>("/repository/status");
}

export function getRepository(): Promise<RepositoryDetails> {
  return apiClient.get<RepositoryDetails>("/repository");
}
