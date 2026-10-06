"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/common/Button";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { Spinner } from "@/components/common/Spinner";

interface RepositoryImportProps {
  isImporting: boolean;
  error: string | null;
  statusError: string | null;
  onImport: (repoUrl: string) => Promise<void>;
}

export function RepositoryImport({
  isImporting,
  error,
  statusError,
  onImport,
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
            disabled={isImporting}
            required
          />
          <p className="import-note">
            Use a public GitHub repository URL. CodeLens clones and indexes the
            repository on the backend.
          </p>
          <Button
            type="submit"
            wide
            disabled={isImporting || !repoUrl.trim()}
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
      </div>
    </main>
  );
}
