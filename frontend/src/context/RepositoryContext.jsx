import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { getBackendHealth } from "../api/repositoryApi";
import {
  askCodebase,
  createChatSession,
  deleteChatSession,
  getChatSessions,
  getChatSession,
  renameChatSession,
} from "../api/chatApi";
import {
  getArchitectureFlows,
  getArchitectureGraph,
} from "../api/architectureApi";
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
    sessions: [],
    sessionId: null,
  });
  const navigate = useNavigate();
  const location = useLocation();
  useEffect(() => {
    getBackendHealth()
      .then(() => setHealth("online"))
      .catch(() => setHealth("offline"));
  }, []);
  useEffect(() => {
    if (location.pathname === "/" && repositoryState.activeRepository)
      navigate("/dashboard", { replace: true });
  }, [location.pathname, repositoryState.activeRepository, navigate]);
  const repositoryPath =
    repositoryState.activeRepository?.repository_path || null;
  useEffect(() => {
    setArchitecture({ result: null, busy: false, error: "", repositoryPath });
    setChat({ messages: [], busy: false, error: "", repositoryPath });
    if (!repositoryPath) return undefined;

    let cancelled = false;
    getChatSessions()
      .then(async ({ sessions }) => {
        if (cancelled) return;
        const session = sessions[0];
        const details = session
          ? await getChatSession(session.session_id)
          : null;
        if (cancelled) return;
        setChat({
          messages: details?.session?.messages || [],
          busy: false,
          error: "",
          repositoryPath,
          sessions,
          sessionId: session?.session_id || null,
        });
      })
      .catch((error) => {
        if (!cancelled) {
          setChat((current) => ({
            ...current,
            error: error.message || "Could not load saved chats.",
          }));
        }
      });
    return () => {
      cancelled = true;
    };
  }, [repositoryPath]);
  async function analyzeArchitecture() {
    setArchitecture((current) => ({ ...current, busy: true, error: "" }));
    try {
      const [flows, graph] = await Promise.all([
        getArchitectureFlows(),
        getArchitectureGraph(),
      ]);
      setArchitecture({
        result: { flows, graph },
        busy: false,
        error: "",
        repositoryPath,
      });
    } catch (error) {
      setArchitecture((current) => ({
        ...current,
        busy: false,
        error: error.message || "Architecture analysis failed.",
      }));
    }
  }
  async function sendChat(question) {
    const content = question.trim();
    if (!content || chat.busy) return;
    if (!repositoryPath) {
      setChat((current) => ({
        ...current,
        error: "Import and activate a repository before starting a chat.",
      }));
      return;
    }
    setChat((current) => ({
      ...current,
      messages: [...current.messages, { role: "user", content }],
      busy: true,
      error: "",
    }));
    try {
      const result = await askCodebase(content, chat.sessionId);
      const sessionId = result.session_id || chat.sessionId;
      setChat((current) => ({
        ...current,
        messages: result.messages || [
          ...current.messages,
          {
            role: "assistant",
            content:
              result.answer ||
              result.response ||
              "The backend returned no answer.",
            sources: result.sources || [],
          },
        ],
        busy: false,
        sessionId,
      }));
      const { sessions } = await getChatSessions();
      setChat((current) => ({ ...current, sessions, sessionId }));
    } catch (error) {
      setChat((current) => ({
        ...current,
        busy: false,
        error: error.message || "Chat request failed.",
      }));
    }
  }
  async function startNewChat() {
    if (!repositoryPath || chat.busy) return;
    try {
      const { session } = await createChatSession();
      setChat((current) => ({
        ...current,
        messages: [],
        sessionId: session.session_id,
        sessions: [session, ...current.sessions],
        error: "",
      }));
    } catch (error) {
      setChat((current) => ({
        ...current,
        error: error.message || "Could not create a new chat.",
      }));
    }
  }
  async function selectChat(sessionId) {
    if (sessionId === chat.sessionId || chat.busy) return;
    try {
      const { session } = await getChatSession(sessionId);
      setChat((current) => ({
        ...current,
        messages: session.messages || [],
        sessionId,
        error: "",
      }));
    } catch (error) {
      setChat((current) => ({
        ...current,
        error: error.message || "Could not load that chat.",
      }));
    }
  }
  async function removeChat(sessionId) {
    if (chat.busy) return;
    try {
      await deleteChatSession(sessionId);
      const remaining = chat.sessions.filter(
        (session) => session.session_id !== sessionId,
      );
      const next = remaining[0];
      if (next) {
        const { session } = await getChatSession(next.session_id);
        setChat((current) => ({
          ...current,
          sessions: remaining,
          sessionId: next.session_id,
          messages: session.messages || [],
          error: "",
        }));
      } else {
        setChat((current) => ({
          ...current,
          sessions: [],
          sessionId: null,
          messages: [],
          error: "",
        }));
      }
    } catch (error) {
      setChat((current) => ({
        ...current,
        error: error.message || "Could not delete that chat.",
      }));
    }
  }
  async function renameChat(sessionId, title) {
    try {
      const { session } = await renameChatSession(sessionId, title);
      setChat((current) => ({
        ...current,
        sessions: current.sessions.map((item) =>
          item.session_id === sessionId ? { ...item, ...session } : item,
        ),
      }));
      return session;
    } catch (error) {
      setChat((current) => ({
        ...current,
        error: error.message || "Could not rename that chat.",
      }));
      throw error;
    }
  }
  const value = useMemo(
    () => ({
      ...repositoryState,
      health,
      architecture,
      analyzeArchitecture,
      chat,
      sendChat,
      startNewChat,
      selectChat,
      removeChat,
      renameChat,
      clearChatError: () => setChat((current) => ({ ...current, error: "" })),
      goToImport: () => navigate("/import"),
      goToDashboard: () => navigate("/dashboard"),
    }),
    [repositoryState, health, architecture, chat, navigate],
  );
  return (
    <RepositoryContext.Provider value={value}>
      {children}
    </RepositoryContext.Provider>
  );
}
export function useRepository() {
  const value = useContext(RepositoryContext);
  if (!value)
    throw new Error("useRepository must be used inside RepositoryProvider");
  return value;
}
