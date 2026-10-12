import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { getBackendHealth } from "../api/repositoryApi";
import { askCodebase } from "../api/chatApi";
import { getArchitectureFlows, getArchitectureGraph } from "../api/architectureApi";
import useRepositories from "../hooks/useRepositories";
const RepositoryContext = createContext(null);
export function RepositoryProvider({ children }) {
  const repositoryState = useRepositories();
  const [health, setHealth] = useState("checking");
  const [architecture, setArchitecture] = useState({
    result: null,
    busy: false,
    error: "",
    repositoryPath: null,
  });
  const [chat, setChat] = useState({
    messages: [],
    busy: false,
    error: "",
    repositoryPath: null,
  });
  const navigate = useNavigate(); const location = useLocation();
  useEffect(() => { getBackendHealth().then(() => setHealth("online")).catch(() => setHealth("offline")); }, []);
  useEffect(() => {
    if (location.pathname === "/" && repositoryState.activeRepository) navigate("/dashboard", { replace: true });
  }, [location.pathname, repositoryState.activeRepository, navigate]);
  const repositoryPath = repositoryState.activeRepository?.repository_path || null;
  useEffect(() => {
    setArchitecture({ result: null, busy: false, error: "", repositoryPath });
    setChat({ messages: [], busy: false, error: "", repositoryPath });
  }, [repositoryPath]);
  async function analyzeArchitecture() {
    setArchitecture((current) => ({ ...current, busy: true, error: "" }));
    try {
      const [flows, graph] = await Promise.all([
        getArchitectureFlows(),
        getArchitectureGraph(),
      ]);
      setArchitecture({ result: { flows, graph }, busy: false, error: "", repositoryPath });
    } catch (error) {
      setArchitecture((current) => ({ ...current, busy: false, error: error.message || "Architecture analysis failed." }));
    }
  }
  async function sendChat(question) {
    const content = question.trim();
    if (!content || chat.busy) return;
    setChat((current) => ({
      ...current,
      messages: [...current.messages, { role: "user", content }],
      busy: true,
      error: "",
    }));
    try {
      const result = await askCodebase(content);
      setChat((current) => ({
        ...current,
        messages: [...current.messages, {
          role: "assistant",
          content: result.answer || result.response || "The backend returned no answer.",
          sources: result.sources || [],
        }],
        busy: false,
      }));
    } catch (error) {
      setChat((current) => ({ ...current, busy: false, error: error.message || "Chat request failed." }));
    }
  }
  const value = useMemo(() => ({
    ...repositoryState, health,
    architecture, analyzeArchitecture,
    chat, sendChat, clearChatError: () => setChat((current) => ({ ...current, error: "" })),
    goToImport: () => navigate("/"),
    goToDashboard: () => navigate("/dashboard"),
  }), [repositoryState, health, architecture, chat, navigate]);
  return <RepositoryContext.Provider value={value}>{children}</RepositoryContext.Provider>;
}
export function useRepository() {
  const value = useContext(RepositoryContext);
  if (!value) throw new Error("useRepository must be used inside RepositoryProvider");
  return value;
}
