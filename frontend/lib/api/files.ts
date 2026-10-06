import { apiClient } from "@/lib/api/client";
import type {
  FileContentResponse,
  FileNode,
  FileTreeResponse,
} from "@/types/files";
import { FALLBACK_FILE_TREE, FALLBACK_FILE_CONTENT } from "@/lib/mock/fallbackData";

export async function getFileTree(): Promise<FileNode[]> {
  try {
    const data = await apiClient.get<FileTreeResponse>("/files/tree", 20_000);
    return data.tree && data.tree.length > 0 ? data.tree : FALLBACK_FILE_TREE;
  } catch (err) {
    console.warn("Using fallback file tree:", err);
    return FALLBACK_FILE_TREE;
  }
}

export async function getFileContent(
  path: string,
): Promise<FileContentResponse> {
  try {
    const encoded = encodeURIComponent(path);
    const data = await apiClient.get<FileContentResponse>(
      `/files/content?path=${encoded}`,
      20_000,
    );
    return data;
  } catch (err) {
    console.warn(`Using fallback content for ${path}:`, err);
    return (
      FALLBACK_FILE_CONTENT[path] || {
        repository: "Nextja_coding_battle",
        path,
        name: path.split("/").pop() || path,
        content: `// Content for ${path}\n// File could not be loaded from backend server.\n\nexport default function File() {\n  return <div>Offline preview</div>;\n}`,
        line_count: 5,
        size: 120,
        chunks: [],
      }
    );
  }
}
