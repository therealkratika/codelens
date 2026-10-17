import { useRepository } from "../context/RepositoryContext";
export default function useChat() {
  const {
    chat,
    sendChat,
    startNewChat,
    selectChat,
    removeChat,
    renameChat,
    clearChatError,
  } = useRepository();
  return {
    messages: chat.messages,
    busy: chat.busy,
    error: chat.error,
    setError: (message) => (!message ? clearChatError() : undefined),
    send: sendChat,
    sessions: chat.sessions,
    sessionId: chat.sessionId,
    newChat: startNewChat,
    selectChat,
    deleteChat: removeChat,
    renameChat,
  };
}
