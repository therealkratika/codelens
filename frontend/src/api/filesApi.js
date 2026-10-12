import { apiRequest } from "./api";

export const getFileTree = () => apiRequest("/api/files/tree");

export const getFileContent = (path) =>
  apiRequest(`/api/files/content?path=${encodeURIComponent(path)}`);
