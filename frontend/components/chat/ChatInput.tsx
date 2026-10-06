"use client";

import { useState, type FormEvent, type KeyboardEvent } from "react";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/common/Button";
import type { ChatMessage as ChatMessageData } from "@/types/ui";

interface ChatInputProps {
  isLoading: boolean;
  onAsk: (question: string) => Promise<void>;
  messages: ChatMessageData[];
  prefilledQuestion?: string;
  onClearPrefill?: () => void;
}

const suggestions = [
  "How is room creation and battle matching implemented?",
  "Where are API requests handled and mapped to routes?",
  "What dependencies does battleController have?",
  "How does the frontend API client talk to the server?",
];

export function ChatInput({
  isLoading,
  onAsk,
  messages,
  prefilledQuestion,
  onClearPrefill,
}: ChatInputProps) {
  const [question, setQuestion] = useState("");
  const [prevPrefill, setPrevPrefill] = useState<string | undefined>(undefined);

  if (prefilledQuestion && prefilledQuestion !== prevPrefill) {
    setPrevPrefill(prefilledQuestion);
    setQuestion(prefilledQuestion);
    onClearPrefill?.();
  }

  async function submitQuestion(value: string) {
    const cleanQuestion = value.trim();
    if (!cleanQuestion || isLoading) {
      return;
    }
    setQuestion("");
    await onAsk(cleanQuestion);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submitQuestion(question);
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      void submitQuestion(question);
    }
  }

  return (
    <div className="chat-entry">
      {messages.length === 0 && !isLoading ? (
        <div className="suggestion-list" aria-label="Suggested questions">
          {suggestions.map((suggestion) => (
            <button
              className="suggestion-button"
              key={suggestion}
              type="button"
              onClick={() => void submitQuestion(suggestion)}
            >
              <Sparkles className="w-3 h-3 text-amber-500 inline mr-1" />
              <span>{suggestion}</span>
            </button>
          ))}
        </div>
      ) : null}
      <form className="chat-composer" onSubmit={handleSubmit}>
        <label htmlFor="chat-question">Ask your codebase</label>
        <textarea
          id="chat-question"
          className="chat-textarea"
          placeholder="Ask about a feature flow, function logic, or API route..."
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          rows={3}
          required
        />
        <div className="composer-footer">
          <span className="composer-hint">Press ⌘+Enter or Ctrl+Enter to send</span>
          <Button type="submit" disabled={isLoading || !question.trim()}>
            {isLoading ? "Analyzing..." : "Ask CodeLens"}
            {!isLoading ? <ArrowRight className="w-3.5 h-3.5 ml-1" /> : null}
          </Button>
        </div>
      </form>
    </div>
  );
}
