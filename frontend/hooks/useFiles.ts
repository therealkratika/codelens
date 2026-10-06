"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { getFileTree, getFileContent } from "@/lib/api/files";
import type { FileNode, FileContentResponse } from "@/types/files";

export function useFiles(initialFilePath?: string | null) {
  const [tree, setTree] = useState<FileNode[]>([]);
  const [selectedFilePath, setSelectedFilePath] = useState<string | null>(
    initialFilePath || null,
  );
  const [fileContent, setFileContent] = useState<FileContentResponse | null>(null);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set(["backend", "frontend"]));
  const [fileSearch, setFileSearch] = useState("");
  const [targetLine, setTargetLine] = useState<number | null>(null);
  const [isLoadingTree, setIsLoadingTree] = useState(true);
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load Tree
  useEffect(() => {
    let cancelled = false;
    async function loadTree() {
      setIsLoadingTree(true);
      try {
        const data = await getFileTree();
        if (!cancelled) {
          setTree(data);
          // Auto select first file if none selected
          const findFirstFile = (nodes: FileNode[]): string | null => {
            for (const n of nodes) {
              if (n.type === "file") return n.path;
              if (n.children) {
                const found = findFirstFile(n.children);
                if (found) return found;
              }
            }
            return null;
          };
          const first = findFirstFile(data);
          if (first) {
            setSelectedFilePath((current) => current || first);
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError("Failed to load file tree.");
          console.error(err);
        }
      } finally {
        if (!cancelled) {
          setIsLoadingTree(false);
        }
      }
    }
    void loadTree();
    return () => {
      cancelled = true;
    };
  }, []);

  // Load Content when selectedFilePath changes
  useEffect(() => {
    if (!selectedFilePath) return;
    let cancelled = false;

    async function loadContent() {
      setIsLoadingContent(true);
      try {
        const data = await getFileContent(selectedFilePath!);
        if (!cancelled) {
          setFileContent(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(`Failed to read file '${selectedFilePath}'.`);
          console.error(err);
        }
      } finally {
        if (!cancelled) {
          setIsLoadingContent(false);
        }
      }
    }

    void loadContent();
    return () => {
      cancelled = true;
    };
  }, [selectedFilePath]);

  const toggleFolder = useCallback((folderPath: string) => {
    setExpandedFolders((prev) => {
      const next = new Set(prev);
      if (next.has(folderPath)) {
        next.delete(folderPath);
      } else {
        next.add(folderPath);
      }
      return next;
    });
  }, []);

  const selectFile = useCallback((path: string, line?: number | null) => {
    setSelectedFilePath(path);
    if (typeof line === "number") {
      setTargetLine(line);
    } else {
      setTargetLine(null);
    }

    // Auto-expand parents
    const parts = path.split("/");
    if (parts.length > 1) {
      setExpandedFolders((prev) => {
        const next = new Set(prev);
        let curr = "";
        for (let i = 0; i < parts.length - 1; i++) {
          curr = curr ? `${curr}/${parts[i]}` : parts[i];
          next.add(curr);
        }
        return next;
      });
    }
  }, []);

  // Count total files in tree
  const totalFileCount = useMemo(() => {
    const count = (nodes: FileNode[]): number => {
      let c = 0;
      for (const n of nodes) {
        if (n.type === "file") c += 1;
        if (n.children) c += count(n.children);
      }
      return c;
    };
    return count(tree);
  }, [tree]);

  return {
    tree,
    selectedFilePath,
    fileContent,
    expandedFolders,
    toggleFolder,
    selectFile,
    fileSearch,
    setFileSearch,
    targetLine,
    setTargetLine,
    totalFileCount,
    isLoadingTree,
    isLoadingContent,
    error,
  };
}
