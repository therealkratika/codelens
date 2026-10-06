export interface ChatRequest {
  question: string;
}

export interface SourceReference {
  file: string;
  start_line: number | null;
  end_line: number | null;
  score?: number;
}

export interface ChatResponse {
  repository: string;
  question: string;
  answer: string;
  sources: SourceReference[];
}
