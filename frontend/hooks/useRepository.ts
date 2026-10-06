"use client";

import { useCallback, useEffect, useState } from "react";

import {
  activateRepository as activateRepositoryRequest,
  getRepository,
  getSavedRepositories,
  getRepositoryStatus,
  importRepository as importRepositoryRequest,
} from "@/lib/api/repository";
import { ApiError } from "@/lib/api/client";
import { getUserError, isGitHubRepositoryUrl } from "@/lib/utils/errors";
import type {
  RepositoryDetails,
  RepositoryImportResponse,
  SavedRepository,
} from "@/types/repository";

interface RepositoryState {
  repository: RepositoryDetails | null;
  importSummary: RepositoryImportResponse | null;
  savedRepositories: SavedRepository[];
  isChecking: boolean;
  isImporting: boolean;
  isActivating: boolean;
  error: string | null;
  statusError: string | null;
  importRepository: (repoUrl: string) => Promise<boolean>;
  activateRepository: (repositoryPath: string) => Promise<boolean>;
}

export function useRepository(): RepositoryState {
  const [repository, setRepository] = useState<RepositoryDetails | null>(null);
  const [importSummary, setImportSummary] =
    useState<RepositoryImportResponse | null>(null);
  const [savedRepositories, setSavedRepositories] = useState<SavedRepository[]>([]);
  const [isChecking, setIsChecking] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [isActivating, setIsActivating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadRepository(): Promise<void> {
      try {
        const status = await getRepositoryStatus();
        if (cancelled) {
          return;
        }
        if (status.loaded) {
          const details = await getRepository();
          if (cancelled) {
            return;
          }
          setRepository(details);
        }

        try {
          const saved = await getSavedRepositories();
          if (!cancelled) {
            setSavedRepositories(saved.repositories);
          }
        } catch (requestError) {
          if (requestError instanceof ApiError && requestError.status === 404) {
            if (!cancelled) {
              setStatusError(
                "The connected backend needs to be restarted or updated to support saved repository switching.",
              );
            }
          } else {
            throw requestError;
          }
        }
      } catch (requestError) {
        if (!cancelled) {
          setStatusError(getUserError(requestError, "status"));
        }
      } finally {
        if (!cancelled) {
          setIsChecking(false);
        }
      }
    }

    void loadRepository();
    return () => {
      cancelled = true;
    };
  }, []);

  const importRepository = useCallback(async (repoUrl: string) => {
    setError(null);
    setStatusError(null);

    if (!isGitHubRepositoryUrl(repoUrl)) {
      setError(
        "Enter a valid GitHub repository URL, such as https://github.com/owner/repository.",
      );
      return false;
    }

    setIsImporting(true);
    try {
      const result = await importRepositoryRequest(repoUrl);
      setImportSummary(result);
      setRepository({
        loaded: true,
        repository: result.repository,
        repository_path: result.repository_path,
      });
      setSavedRepositories((currentRepositories) => [
        ...currentRepositories.filter(
          (repository) =>
            repository.repository_path !== result.repository_path,
        ),
        {
          repository: result.repository,
          repository_path: result.repository_path,
          repo_url: result.repo_url,
          files: result.files,
          chunks: result.chunks,
        },
      ]);
      return true;
    } catch (requestError) {
      setError(getUserError(requestError, "import"));
      return false;
    } finally {
      setIsImporting(false);
    }
  }, []);

  const activateRepository = useCallback(async (repositoryPath: string) => {
    setError(null);
    setStatusError(null);
    setIsActivating(true);
    try {
      const details = await activateRepositoryRequest(repositoryPath);
      setRepository(details);
      return true;
    } catch (requestError) {
      setError(getUserError(requestError, "activate"));
      return false;
    } finally {
      setIsActivating(false);
    }
  }, []);

  return {
    repository,
    importSummary,
    savedRepositories,
    isChecking,
    isImporting,
    isActivating,
    error,
    statusError,
    importRepository,
    activateRepository,
  };
}
