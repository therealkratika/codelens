import { apiRequest } from "./api";

export const getBackendHealth = () => apiRequest("/");
export const getSavedRepositories = () => apiRequest("/api/repository/saved");
export const getRepositoryStatus = () => apiRequest("/api/repository/status");
export const importRepository = (repoUrl) =>
  apiRequest("/api/repository/import", { method: "POST", body: JSON.stringify({ repo_url: repoUrl }) });
export const getImportStatus = (jobId) =>
  apiRequest(`/api/repository/import/${encodeURIComponent(jobId)}`);
export const activateRepository = (repositoryPath) =>
  apiRequest("/api/repository/activate", { method: "POST", body: JSON.stringify({ repository_path: repositoryPath }) });
