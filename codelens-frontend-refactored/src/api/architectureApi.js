import { apiRequest } from "./api";

/*
 * Current backend contract in this project does not yet expose a dedicated
 * architecture endpoint. This function deliberately uses the existing RAG chat
 * endpoint to request a repository-grounded architecture summary.
 */
export const getArchitectureSummary = () =>
  apiRequest("/api/chat", {
    method: "POST",
    body: JSON.stringify({
      question: "Analyze this repository's architecture. Explain the main modules, entry points, data flow, dependencies, and how the frontend and backend communicate. Clearly distinguish evidence from assumptions and cite relevant source files."
    }),
  });
