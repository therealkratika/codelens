"use client";

import { MessageSquareCode, Trash2 } from "lucide-react";
import { ChatInput } from "@/components/chat/ChatInput";
import { ChatMessage } from "@/components/chat/ChatMessage";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import type { ChatMessage as ChatMessageData } from "@/types/ui";

interface ChatInterfaceProps {
  messages: ChatMessageData[];
  isLoading: boolean;
  error: string | null;
  prefilledQuestion?: string;
  onAsk: (question: string) => Promise<void>;
  onClearError: () => void;
  onClearChat?: () => void;
  onOpenFile?: (file: string, line?: number) => void;
  onClearPrefill?: () => void;
}

export function ChatInterface({
  messages,
  isLoading,
  error,
  prefilledQuestion,
  onAsk,
  onClearError,
  onClearChat,
  onOpenFile,
  onClearPrefill,
}: ChatInterfaceProps) {
  return (
    <section className="page-container chat-page">
      <header className="chat-heading-row">
        <div className="chat-heading">
          <p className="eyebrow">Repository Q&amp;A</p>
          <h1>Ask Your Codebase</h1>
          <p>
            Answers are grounded in indexed code, with verifiable source references.
          </p>
        </div>

        {messages.length > 0 && onClearChat && (
          <button
            type="button"
            className="btn-clear-chat"
            onClick={onClearChat}
            title="Clear conversation history"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Clear conversation</span>
          </button>
        )}
      </header>

      {error ? (
        <div className="chat-error">
          <ErrorMessage message={error} onDismiss={onClearError} />
        </div>
      ) : null}

      <div className="conversation" aria-live="polite">
        {messages.length === 0 ? (
          <div className="conversation-empty">
            <div className="empty-state">
              <span className="empty-symbol" aria-hidden="true">
                <MessageSquareCode className="w-6 h-6 text-accent" />
              </span>
              <h2>Explore this codebase</h2>
              <p>
                Ask a technical question about feature implementations, API routes,
                controllers, or how backend services connect.
              </p>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <ChatMessage
              key={message.id}
              message={message}
              isLoading={isLoading && index === messages.length - 1}
              onOpenFile={onOpenFile}
            />
          ))
        )}
      </div>

      <ChatInput
        messages={messages}
        isLoading={isLoading}
        onAsk={onAsk}
        prefilledQuestion={prefilledQuestion}
        onClearPrefill={onClearPrefill}
      />
    </section>
  );
}
