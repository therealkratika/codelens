export interface RepositoryImportRequest {
  repo_url: string;
}

export interface RepositoryImportResponse {
  repository: string;
  repository_path: string;
  repo_url: string;
  files: number;
  chunks: number;
  status: "indexed";
}

export type RepositoryImportJob =
  | {
      job_id: string;
      status: "queued" | "running";
      result: null;
      error: null;
    }
  | {
      job_id: string;
      status: "completed";
      result: RepositoryImportResponse;
      error: null;
    }
  | {
      job_id: string;
      status: "failed";
      result: null;
      error: string;
    };

export type RepositoryStatus =
  | {
      loaded: false;
      repository: null;
    }
  | {
      loaded: true;
      repository: string;
      repository_path: string;
    };

export interface RepositoryDetails {
  loaded: true;
  repository: string;
  repository_path: string;
}

export interface SavedRepository {
  repository: string;
  repository_path: string;
  repo_url: string | null;
  files: number;
  chunks: number;
}

export interface SavedRepositoriesResponse {
  repositories: SavedRepository[];
  active_repository_path: string | null;
}

export interface RepositorySuggestionsResponse {
  repository: string;
  suggestions: string[];
}
