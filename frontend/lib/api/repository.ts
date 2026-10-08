import { ApiError, ApiTimeoutError, apiClient } from "@/lib/api/client";
import type {
  RepositoryDetails,
  RepositoryImportJob,
  RepositoryImportRequest,
  RepositoryImportResponse,
  RepositorySuggestionsResponse,
  SavedRepositoriesResponse,
  RepositoryStatus,
} from "@/types/repository";

export function importRepository(
  repoUrl: string,
): Promise<RepositoryImportResponse> {
  return startAndWaitForRepositoryImport(repoUrl);
}

async function startAndWaitForRepositoryImport(
  repoUrl: string,
): Promise<RepositoryImportResponse> {
  const request: RepositoryImportRequest = { repo_url: repoUrl };
  let job = await apiClient.post<
    RepositoryImportJob,
    RepositoryImportRequest
  >("/repository/import", request);
  const deadline = Date.now() + 30 * 60 * 1000;

  while (true) {
    if (job.status === "completed") {
      return job.result;
    }
    if (job.status === "failed") {
      throw new ApiError(500, job.error);
    }
    if (Date.now() >= deadline) {
      throw new ApiTimeoutError();
    }

    await new Promise((resolve) => window.setTimeout(resolve, 2_000));
    job = await apiClient.get<RepositoryImportJob>(
      `/repository/import/${encodeURIComponent(job.job_id)}`,
    );
  }
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
