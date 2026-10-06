import type { RepositoryDetails } from "@/types/repository";

interface RepositoryHeaderProps {
  repository: RepositoryDetails;
}

export function RepositoryHeader({ repository }: RepositoryHeaderProps) {
  return (
    <div className="repository-title-row">
      <div className="repository-title">
        <span className="repository-icon" aria-hidden="true">⌘</span>
        <div>
          <h2>{repository.repository}</h2>
          <div className="repository-path">{repository.repository_path}</div>
        </div>
      </div>
      <span className="indexed-badge">Indexed</span>
    </div>
  );
}
