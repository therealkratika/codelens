import { apiClient } from "@/lib/api/client";
import type { ChatRequest, ChatResponse } from "@/types/chat";

export function askQuestion(question: string): Promise<ChatResponse> {
  const request: ChatRequest = { question };
  return apiClient.post<ChatResponse, ChatRequest>(
    "/chat",
    request,
    240_000,
  );
}
