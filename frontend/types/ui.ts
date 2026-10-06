import type { SourceReference } from "@/types/chat";

export type WorkspaceView = "overview" | "chat" | "architecture" | "files";

export interface ChatMessage {
  id: string;
  question: string;
  answer: string | null;
  sources: SourceReference[];
}
