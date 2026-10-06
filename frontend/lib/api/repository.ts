import { apiClient } from "@/lib/api/client";
import type {
  RepositoryDetails,
  RepositoryImportRequest,
  RepositoryImportResponse,
  RepositorySuggestionsResponse,
  SavedRepositoriesResponse,
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

export function getRepositorySuggestions(): Promise<RepositorySuggestionsResponse> {
  return apiClient.get<RepositorySuggestionsResponse>(
    "/repository/suggestions",
  );
}

export function getSavedRepositories(): Promise<SavedRepositoriesResponse> {
  return apiClient.get<SavedRepositoriesResponse>("/repository/saved");
}

export function activateRepository(
  repositoryPath: string,
): Promise<RepositoryDetails> {
  return apiClient.post<
    RepositoryDetails,
    { repository_path: string }
  >("/repository/activate", { repository_path: repositoryPath }, 600_000);
}
