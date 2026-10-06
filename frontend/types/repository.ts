export interface RepositoryImportRequest {
  repo_url: string;
}

export interface RepositoryImportResponse {
  repository: string;
  repository_path: string;
  files: number;
  chunks: number;
  status: "indexed";
}

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
