import { apiRequest } from "./api";
export const askCodebase = (question, sessionId) =>
  apiRequest("/api/chat", {
    method: "POST",
    body: JSON.stringify({
      question,
      ...(sessionId ? { session_id: sessionId } : {}),
    }),
  });

export const getChatSessions = () => apiRequest("/api/chat/sessions");
export const getChatSession = (sessionId) =>
  apiRequest(`/api/chat/sessions/${encodeURIComponent(sessionId)}`);
export const createChatSession = (title) =>
  apiRequest("/api/chat/sessions", {
    method: "POST",
    body: JSON.stringify(title ? { title } : {}),
  });
export const deleteChatSession = (sessionId) =>
  apiRequest(`/api/chat/sessions/${encodeURIComponent(sessionId)}`, {
    method: "DELETE",
  });
export const renameChatSession = (sessionId, title) =>
  apiRequest(`/api/chat/sessions/${encodeURIComponent(sessionId)}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
