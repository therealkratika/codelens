"use client";

import { useCallback, useState } from "react";

import { askQuestion } from "@/lib/api/chat";
import { getUserError } from "@/lib/utils/errors";
import type { ChatMessage } from "@/types/ui";

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  ask: (question: string) => Promise<void>;
  clearError: () => void;
  clearChat: () => void;
}

export function useChat(): ChatState {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = useCallback(async (question: string) => {
    const cleanQuestion = question.trim();
    if (!cleanQuestion || isLoading) {
      return;
    }

    const messageId = crypto.randomUUID();
    setError(null);
    setIsLoading(true);
    setMessages((current) => [
      ...current,
      {
        id: messageId,
        question: cleanQuestion,
        answer: null,
        sources: [],
      },
    ]);

    try {
      const response = await askQuestion(cleanQuestion);
      setMessages((current) =>
        current.map((message) =>
          message.id === messageId
            ? {
                ...message,
                answer: response.answer,
                sources: response.sources,
              }
            : message,
        ),
      );
    } catch (requestError) {
      setError(getUserError(requestError, "chat"));
      setMessages((current) =>
        current.filter((message) => message.id !== messageId),
      );
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  const clearError = useCallback(() => setError(null), []);
  const clearChat = useCallback(() => setMessages([]), []);

  return { messages, isLoading, error, ask, clearError, clearChat };
}
