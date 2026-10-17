import { useEffect, useRef, useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import ChatMessage from "../components/chat/ChatMessage";
import ChatInput from "../components/chat/ChatInput";
import Loader from "../components/common/Loader";
import Button from "../components/common/Button";
import { useRepository } from "../context/RepositoryContext";
import useChat from "../hooks/useChat";
export default function ChatPage() {
  const { activeRepository, goToImport } = useRepository();
  const {
    messages,
    busy,
    error,
    setError,
    send,
    sessions,
    sessionId,
    newChat,
    selectChat,
    deleteChat,
    renameChat,
  } = useChat();
  const [renaming, setRenaming] = useState(false);
  const [chatName, setChatName] = useState("");
  const bottom = useRef(null);
  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);
  const currentSession = sessions.find(
    (session) => session.session_id === sessionId,
  );
  function beginRename() {
    setChatName(currentSession?.title || "");
    setRenaming(true);
  }
  async function saveName(event) {
    event.preventDefault();
    const title = chatName.trim();
    if (!title || !sessionId) return;
    await renameChat(sessionId, title);
    setRenaming(false);
  }
  return (
    <>
      <PageHeader
        eyebrow="ASK QUESTIONS, GET CONTEXT"
        title="Code chat"
        description="Ask questions grounded in your active repository."
      />
      <section className="card chat-layout">
        <div className="chat-main">
          <div className="chat-header">
            <div className="chat-bot-avatar">✳</div>
            <div>
              <strong>CodeLens assistant</strong>
              <p>
                {activeRepository
                  ? `Grounded in ${activeRepository.repository}`
                  : "No active repository"}
              </p>
            </div>
            <span className="chat-context-badge">RAG powered</span>
          </div>
          <div className="chat-session-toolbar">
            <div className="chat-session-picker">
              <span className="chat-session-label">Conversation</span>
              <select
                value={sessionId || ""}
                onChange={(event) => selectChat(event.target.value)}
                disabled={busy || !sessions.length}
                aria-label="Saved chats"
              >
                {!sessions.length && <option value="">No saved chats</option>}
                {sessions.map((session) => (
                  <option key={session.session_id} value={session.session_id}>
                    {session.title}
                  </option>
                ))}
              </select>
            </div>
            <div className="chat-session-actions">
              <Button onClick={newChat} disabled={busy || !activeRepository}>
                + New chat
              </Button>
              {sessionId && (
                <>
                  <Button
                    variant="outline"
                    onClick={beginRename}
                    disabled={busy}
                  >
                    Rename
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => deleteChat(sessionId)}
                    disabled={busy}
                  >
                    Delete
                  </Button>
                </>
              )}
            </div>
          </div>
          {renaming && (
            <form className="chat-rename-form" onSubmit={saveName}>
              <label htmlFor="chat-name">Chat name</label>
              <input
                id="chat-name"
                value={chatName}
                maxLength={120}
                autoFocus
                onChange={(event) => setChatName(event.target.value)}
                placeholder="e.g. Authentication flow"
              />
              <Button type="submit" disabled={!chatName.trim()}>
                Save
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => setRenaming(false)}
              >
                Cancel
              </Button>
            </form>
          )}
          <div className="chat-messages">
            {!messages.length ? (
              <div className="chat-empty">
                <div className="chat-empty-symbol">✳</div>
                <h2>What would you like to understand?</h2>
                <p className="muted">
                  Ask about architecture, functions, authentication, or data
                  flow.
                </p>
                {!activeRepository && (
                  <Button onClick={goToImport}>Import repository →</Button>
                )}
                <div className="suggestion-list">
                  {[
                    "Explain the overall architecture",
                    "Where is authentication handled?",
                    "How does the frontend communicate with the backend?",
                  ].map((q) => (
                    <button
                      className="suggestion"
                      key={q}
                      disabled={!activeRepository || busy}
                      onClick={() => send(q)}
                    >
                      ✧ {q}
                      <span className="suggestion-arrow">↗</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((message, i) => (
                <ChatMessage key={i} message={message} />
              ))
            )}
            {busy && <Loader label="CodeLens is thinking…" />}
            <div ref={bottom} />
          </div>
          {error && (
            <div className="alert alert-error">
              {error}
              <button onClick={() => setError("")}>×</button>
            </div>
          )}
          <ChatInput disabled={!activeRepository || busy} onSend={send} />
        </div>
        <aside className="chat-aside">
          <p className="eyebrow">CHAT CONTEXT</p>
          <h3>Repository details</h3>
          {activeRepository ? (
            <>
              <div className="context-repo-icon">⌘</div>
              <strong>{activeRepository.repository}</strong>
              <p className="muted context-path">
                {activeRepository.repository_path}
              </p>
              <div className="context-divider" />
              <div className="context-info">
                <span>Status</span>
                <strong className="text-success">● Active</strong>
              </div>
            </>
          ) : (
            <p className="muted">
              Import and activate a repository to provide code context.
            </p>
          )}
          <div className="context-tip">
            <strong>Tip for better answers</strong>
            <p>Ask specific questions about files, functions, and data flow.</p>
          </div>
        </aside>
      </section>
    </>
  );
}
