import os
from typing import Dict, List, Any, Optional
from app.rag.vector_store import VectorStore


class FileService:
    def __init__(self, repository_path: str):
        self.repository_path = repository_path
        self.vector_store = VectorStore(repository_path)
        self._chunks_by_file: Optional[Dict[str, List[Dict[str, Any]]]] = None

    def _load_chunks(self) -> Dict[str, List[Dict[str, Any]]]:
        if self._chunks_by_file is not None:
            return self._chunks_by_file

        chunks_map: Dict[str, List[Dict[str, Any]]] = {}
        try:
            data = self.vector_store.collection.get(include=["metadatas"])
            for meta in data.get("metadatas", []):
                fp = meta.get("file")
                if not fp:
                    continue
                if fp not in chunks_map:
                    chunks_map[fp] = []
                chunks_map[fp].append({
                    "start_line": meta.get("start_line", 1),
                    "end_line": meta.get("end_line", 1)
                })
        except Exception as e:
            print(f"Error loading chunks from vector store: {e}")

        # Sort chunks by start line
        for fp in chunks_map:
            chunks_map[fp].sort(key=lambda x: x["start_line"])

        self._chunks_by_file = chunks_map
        return chunks_map

    def get_file_tree(self) -> List[Dict[str, Any]]:
        ignored = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".next", "coverage", ".cache", "out", "target"}
        chunks_map = self._load_chunks()

        def build_node(current_path: str, rel_path: str) -> Optional[Dict[str, Any]]:
            name = os.path.basename(current_path)
            if name in ignored or (os.path.isdir(current_path) and name.startswith(".")):
                return None

            if os.path.isdir(current_path):
                children = []
                try:
                    entries = sorted(os.listdir(current_path), key=lambda x: (not os.path.isdir(os.path.join(current_path, x)), x.lower()))
                    for entry in entries:
                        child_path = os.path.join(current_path, entry)
                        child_rel = os.path.relpath(child_path, self.repository_path).replace(os.sep, "/")
                        child_node = build_node(child_path, child_rel)
                        if child_node is not None:
                            children.append(child_node)
                except OSError:
                    pass

                return {
                    "name": name,
                    "path": rel_path if rel_path != "." else "",
                    "type": "directory",
                    "children": children
                }
            else:
                try:
                    size = os.path.getsize(current_path)
                    ext = os.path.splitext(name)[1].lower()
                    chunk_list = chunks_map.get(rel_path, [])
                    return {
                        "name": name,
                        "path": rel_path,
                        "type": "file",
                        "size": size,
                        "extension": ext,
                        "chunk_count": len(chunk_list)
                    }
                except OSError:
                    return None

        root_node = build_node(self.repository_path, ".")
        return root_node.get("children", []) if root_node and "children" in root_node else []

    def get_file_content(self, relative_path: str) -> Dict[str, Any]:
        # Normalize and guard against directory traversal
        clean_rel = relative_path.lstrip("/").replace("\\", "/")
        full_path = os.path.abspath(os.path.join(self.repository_path, clean_rel))
        repo_abs = os.path.abspath(self.repository_path)

        if not full_path.startswith(repo_abs):
            raise ValueError("Path is outside the repository")

        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            raise FileNotFoundError(f"File '{clean_rel}' does not exist")

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        lines = content.splitlines()
        chunks_map = self._load_chunks()
        file_chunks = chunks_map.get(clean_rel, [])

        return {
            "path": clean_rel,
            "name": os.path.basename(clean_rel),
            "content": content,
            "line_count": len(lines),
            "size": len(content.encode("utf-8")),
            "chunks": file_chunks
        }
