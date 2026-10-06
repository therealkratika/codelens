"use client";

import { useCallback, useEffect, useState } from "react";

import {
  getRepository,
  getRepositoryStatus,
  importRepository as importRepositoryRequest,
} from "@/lib/api/repository";
import { getUserError, isGitHubRepositoryUrl } from "@/lib/utils/errors";
import type {
  RepositoryDetails,
  RepositoryImportResponse,
} from "@/types/repository";

interface RepositoryState {
  repository: RepositoryDetails | null;
  importSummary: RepositoryImportResponse | null;
  isChecking: boolean;
  isImporting: boolean;
  error: string | null;
  statusError: string | null;
  importRepository: (repoUrl: string) => Promise<void>;
}

export function useRepository(): RepositoryState {
  const [repository, setRepository] = useState<RepositoryDetails | null>(null);
  const [importSummary, setImportSummary] =
    useState<RepositoryImportResponse | null>(null);
  const [isChecking, setIsChecking] = useState(true);
  const [isImporting, setIsImporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadRepository(): Promise<void> {
      try {
        const status = await getRepositoryStatus();
        if (cancelled || !status.loaded) {
          return;
        }
        const details = await getRepository();
        if (!cancelled) {
          setRepository(details);
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
      return;
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
    } catch (requestError) {
      setError(getUserError(requestError, "import"));
    } finally {
      setIsImporting(false);
    }
  }, []);

  return {
    repository,
    importSummary,
    isChecking,
    isImporting,
    error,
    statusError,
    importRepository,
  };
}
