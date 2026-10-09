import { apiRequest } from "./api";
export const askCodebase = (question) =>
  apiRequest("/api/chat", { method: "POST", body: JSON.stringify({ question }) });
