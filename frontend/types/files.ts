export interface FileChunk {
  start_line: number;
  end_line: number;
}

export interface FileNode {
  name: string;
  path: string;
  type: "file" | "directory";
  size?: number;
  extension?: string;
  chunk_count?: number;
  children?: FileNode[];
}

export interface FileContentResponse {
  repository: string;
  path: string;
  name: string;
  content: string;
  line_count: number;
  size: number;
  chunks: FileChunk[];
}

export interface FileTreeResponse {
  repository: string;
  tree: FileNode[];
}
