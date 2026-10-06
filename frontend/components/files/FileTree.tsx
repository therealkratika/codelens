"use client";

import { useMemo } from "react";
import {
  ChevronDown,
  ChevronRight,
  File,
  FileCode,
  FileJson,
  FileSpreadsheet,
  FileText,
  Folder,
  FolderOpen,
  Search,
} from "lucide-react";
import type { FileNode } from "@/types/files";

interface FileTreeProps {
  tree: FileNode[];
  selectedFilePath: string | null;
  expandedFolders: Set<string>;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onToggleFolder: (path: string) => void;
  onSelectFile: (path: string) => void;
}

function getFileIcon(extension?: string) {
  switch (extension) {
    case ".ts":
    case ".tsx":
      return <FileCode className="w-4 h-4 text-emerald-500 flex-shrink-0" />;
    case ".js":
    case ".jsx":
      return <FileCode className="w-4 h-4 text-amber-500 flex-shrink-0" />;
    case ".json":
      return <FileJson className="w-4 h-4 text-emerald-500 flex-shrink-0" />;
    case ".md":
      return <FileText className="w-4 h-4 text-stone-400 flex-shrink-0" />;
    case ".css":
    case ".scss":
      return <FileSpreadsheet className="w-4 h-4 text-amber-400 flex-shrink-0" />;
    case ".py":
      return <FileCode className="w-4 h-4 text-lime-500 flex-shrink-0" />;
    default:
      return <File className="w-4 h-4 text-muted flex-shrink-0" />;
  }
}

interface TreeNodeItemProps {
  node: FileNode;
  level: number;
  selectedFilePath: string | null;
  expandedFolders: Set<string>;
  searchQuery: string;
  onToggleFolder: (path: string) => void;
  onSelectFile: (path: string) => void;
}

function TreeNodeItem({
  node,
  level,
  selectedFilePath,
  expandedFolders,
  searchQuery,
  onToggleFolder,
  onSelectFile,
}: TreeNodeItemProps) {
  const isDirectory = node.type === "directory";
  const isExpanded = expandedFolders.has(node.path);
  const isSelected = selectedFilePath === node.path;

  // Filter visibility if search active
  const hasMatchingChild = useMemo(() => {
    if (!searchQuery.trim() || !isDirectory) return true;
    const q = searchQuery.toLowerCase();
    const check = (n: FileNode): boolean => {
      if (n.name.toLowerCase().includes(q)) return true;
      if (n.children) {
        return n.children.some(check);
      }
      return false;
    };
    return check(node);
  }, [node, searchQuery, isDirectory]);

  if (!hasMatchingChild) return null;

  return (
    <div className="tree-node-wrapper">
      <button
        type="button"
        className={`tree-node-row ${isSelected ? "is-selected" : ""}`}
        style={{ paddingLeft: `${Math.max(10, level * 14 + 10)}px` }}
        onClick={() => {
          if (isDirectory) {
            onToggleFolder(node.path);
          } else {
            onSelectFile(node.path);
          }
        }}
      >
        <span className="tree-node-arrow">
          {isDirectory ? (
            isExpanded ? (
              <ChevronDown className="w-3.5 h-3.5" />
            ) : (
              <ChevronRight className="w-3.5 h-3.5" />
            )
          ) : (
            <span className="w-3.5 h-3.5 inline-block" />
          )}
        </span>

        <span className="tree-node-icon">
          {isDirectory ? (
            isExpanded ? (
              <FolderOpen className="w-4 h-4 text-sky-500" />
            ) : (
              <Folder className="w-4 h-4 text-sky-400" />
            )
          ) : (
            getFileIcon(node.extension)
          )}
        </span>

        <span className="tree-node-label" title={node.path}>
          {node.name}
        </span>

        {!isDirectory && typeof node.chunk_count === "number" && node.chunk_count > 0 && (
          <span
            className="tree-chunk-badge"
            title={`${node.chunk_count} code chunks indexed in vector store`}
          >
            {node.chunk_count}c
          </span>
        )}
      </button>

      {isDirectory && (isExpanded || searchQuery.trim().length > 0) && node.children && (
        <div className="tree-children-container">
          {node.children.map((child) => (
            <TreeNodeItem
              key={child.path}
              node={child}
              level={level + 1}
              selectedFilePath={selectedFilePath}
              expandedFolders={expandedFolders}
              searchQuery={searchQuery}
              onToggleFolder={onToggleFolder}
              onSelectFile={onSelectFile}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function FileTree({
  tree,
  selectedFilePath,
  expandedFolders,
  searchQuery,
  onSearchChange,
  onToggleFolder,
  onSelectFile,
}: FileTreeProps) {
  return (
    <div className="file-tree-container">
      <div className="file-tree-search-bar">
        <Search className="w-4 h-4 search-icon" />
        <input
          type="text"
          className="file-search-input"
          placeholder="Filter files..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      <div className="file-tree-nodes">
        {tree.length === 0 ? (
          <div className="file-tree-empty">
            <p>No files indexed in repository.</p>
          </div>
        ) : (
          tree.map((node) => (
            <TreeNodeItem
              key={node.path}
              node={node}
              level={0}
              selectedFilePath={selectedFilePath}
              expandedFolders={expandedFolders}
              searchQuery={searchQuery}
              onToggleFolder={onToggleFolder}
              onSelectFile={onSelectFile}
            />
          ))
        )}
      </div>
    </div>
  );
}
