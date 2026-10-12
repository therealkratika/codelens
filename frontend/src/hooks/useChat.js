import { useRepository } from "../context/RepositoryContext";
export default function useChat() {
  const { chat, sendChat, clearChatError } = useRepository();
  return {
    messages: chat.messages,
    busy: chat.busy,
    error: chat.error,
    setError: (message) => (message ? undefined : clearChatError()),
    send: sendChat,
  };
}
