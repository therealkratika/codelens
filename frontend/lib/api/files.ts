import { apiClient } from "@/lib/api/client";
import type {
  FileContentResponse,
  FileNode,
  FileTreeResponse,
} from "@/types/files";

export async function getFileTree(): Promise<FileNode[]> {
  const data = await apiClient.get<FileTreeResponse>("/files/tree", 20_000);
  return data.tree;
}

export async function getFileContent(
  path: string,
): Promise<FileContentResponse> {
  const encoded = encodeURIComponent(path);
  return apiClient.get<FileContentResponse>(
    `/files/content?path=${encoded}`,
    20_000,
  );
}
