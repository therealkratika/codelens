import { useCallback, useEffect, useState } from "react";
import {
  getSavedRepositories,
  getRepositoryStatus,
  activateRepository,
} from "../api/repositoryApi";
export default function useRepositories() {
  const [repositories, setRepositories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeRepository, setActiveRepository] = useState(null);
  const [error, setError] = useState("");
  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const [saved, status] = await Promise.all([
        getSavedRepositories(),
        getRepositoryStatus(),
      ]);
      const list = Array.isArray(saved.repositories) ? saved.repositories : [];
      setRepositories(list);
      if (status.loaded && status.repository_path) {
        const metadata = list.find(
          (repo) => repo.repository_path === status.repository_path,
        );
        setActiveRepository({
          ...(metadata || {}),
          repository:
            metadata?.repository || status.repository || "Active repository",
          repository_path: status.repository_path,
        });
      } else {
        setActiveRepository(null);
      }
      setError("");
      return { list, status };
    } catch (e) {
      setError(e.message || "Could not load repository data.");
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);
  const activate = useCallback(
    async (path) => {
      const result = await activateRepository(path);
      setActiveRepository({
        repository:
          result.repository || result.repository_name || "Active repository",
        repository_path: result.repository_path || path,
      });
      await refresh();
      return result;
    },
    [refresh],
  );
  useEffect(() => {
    refresh().catch(() => {});
  }, [refresh]);
  return {
    repositories,
    loading,
    activeRepository,
    setActiveRepository,
    error,
    setError,
    refresh,
    activate,
  };
}
