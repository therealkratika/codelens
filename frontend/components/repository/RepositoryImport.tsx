"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/common/Button";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { Spinner } from "@/components/common/Spinner";
import type { SavedRepository } from "@/types/repository";

interface RepositoryImportProps {
  isImporting: boolean;
  isActivating: boolean;
  error: string | null;
  statusError: string | null;
  savedRepositories: SavedRepository[];
  activeRepositoryPath: string | null;
  onImport: (repoUrl: string) => Promise<boolean>;
  onActivate: (repositoryPath: string) => Promise<boolean>;
}

export function RepositoryImport({
  isImporting,
  isActivating,
  error,
  statusError,
  savedRepositories,
  activeRepositoryPath,
  onImport,
  onActivate,
}: RepositoryImportProps) {
  const [repoUrl, setRepoUrl] = useState("");

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void onImport(repoUrl.trim());
  }

  return (
    <main className="import-page">
      <div className="import-content">
        <div className="import-heading">
          <span className="brand-mark" aria-hidden="true">C</span>
          <p className="eyebrow">CodeLens workspace</p>
          <h1>Bring your codebase into focus.</h1>
          <p>
            Import a GitHub repository to ask questions and trace answers back
            to the code.
          </p>
        </div>

        <form className="panel import-panel" onSubmit={handleSubmit}>
          {statusError ? <ErrorMessage message={statusError} /> : null}
          {error ? <ErrorMessage message={error} /> : null}
          <label htmlFor="repository-url">GitHub repository</label>
          <input
            id="repository-url"
            className="input"
            type="url"
            autoComplete="url"
            placeholder="https://github.com/owner/repository"
            value={repoUrl}
            onChange={(event) => setRepoUrl(event.target.value)}
            disabled={isImporting || isActivating}
            required
          />
          <p className="import-note">
            Use a public GitHub repository URL. CodeLens clones and indexes the
            repository on the backend.
          </p>
          <Button
            type="submit"
            wide
            disabled={isImporting || isActivating || !repoUrl.trim()}
          >
            {isImporting ? (
              <>
                <Spinner label="Importing repository" />
                Importing repository...
              </>
            ) : (
              "Import repository"
            )}
          </Button>
          {isImporting ? (
            <div className="import-loading" aria-live="polite">
              <Spinner />
              <div>
                <strong>Indexing repository</strong>
                <span>
                  Cloning files, creating embeddings and building the code
                  search index. This may take a few minutes.
                </span>
              </div>
            </div>
          ) : null}
        </form>
        {savedRepositories.length > 0 ? (
          <section className="panel import-panel" aria-labelledby="saved-repositories-heading">
            <h2 id="saved-repositories-heading">Your repositories</h2>
            <p className="import-note">
              Repositories stay indexed on this backend. Select one to switch
              without importing it again.
            </p>
            <ul className="saved-repository-list">
              {savedRepositories.map((repository) => {
                const isActive =
                  repository.repository_path === activeRepositoryPath;
                return (
                  <li key={repository.repository_path}>
                    <div>
                      <strong>{repository.repository}</strong>
                      {repository.repo_url ? (
                        <span>{repository.repo_url}</span>
                      ) : (
                        <span>Local repository</span>
                      )}
                    </div>
                    <Button
                      type="button"
                      disabled={isImporting || isActivating || isActive}
                      onClick={() => void onActivate(repository.repository_path)}
                    >
                      {isActivating && !isActive
                        ? "Switching..."
                        : isActive
                          ? "Current"
                          : "Switch"}
                    </Button>
                  </li>
                );
              })}
            </ul>
          </section>
        ) : null}
      </div>
    </main>
  );
}
