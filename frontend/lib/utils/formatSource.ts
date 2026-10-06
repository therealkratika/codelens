import type { SourceReference } from "@/types/chat";

export function formatSourceLines(source: SourceReference): string {
  const { start_line: startLine, end_line: endLine } = source;

  if (startLine == null) {
    return "Line range unavailable";
  }

  if (endLine == null || startLine === endLine) {
    return `Line ${startLine}`;
  }

  return `Lines ${startLine}-${endLine}`;
}
