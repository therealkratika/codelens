import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { getBackendHealth } from "../api/repositoryApi";
import useRepositories from "../hooks/useRepositories";
const RepositoryContext = createContext(null);
export function RepositoryProvider({ children }) {
  const repositoryState = useRepositories();
  const [health, setHealth] = useState("checking");
  const navigate = useNavigate(); const location = useLocation();
  useEffect(() => { getBackendHealth().then(() => setHealth("online")).catch(() => setHealth("offline")); }, []);
  useEffect(() => {
    if (location.pathname === "/" && repositoryState.activeRepository) navigate("/dashboard", { replace: true });
  }, [location.pathname, repositoryState.activeRepository, navigate]);
  const value = useMemo(() => ({
    ...repositoryState, health,
    goToImport: () => navigate("/"),
    goToDashboard: () => navigate("/dashboard"),
  }), [repositoryState, health, navigate]);
  return <RepositoryContext.Provider value={value}>{children}</RepositoryContext.Provider>;
}
export function useRepository() {
  const value = useContext(RepositoryContext);
  if (!value) throw new Error("useRepository must be used inside RepositoryProvider");
  return value;
}
