import { apiRequest } from "./api";

/*
 * The current backend returns aggregate chunk counts in saved repository metadata,
 * but no confirmed endpoint for listing individual chunks. This uses the existing
 * chat endpoint for an explanation of the indexing/retrieval pipeline; it does not
 * pretend to fetch actual chunk records.
 */
export const explainChunkIndex = () =>
  apiRequest("/api/chat", {
    method: "POST",
    body: JSON.stringify({
      question: "Explain how this repository is indexed for retrieval: identify relevant files, chunking strategy, embedding/vector store flow, and retrieval pipeline. Only report details supported by repository source context."
    }),
  });
