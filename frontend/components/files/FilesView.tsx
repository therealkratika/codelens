"use client";

import { useFiles } from "@/hooks/useFiles";
import { FileTree } from "@/components/files/FileTree";
import { CodeViewer } from "@/components/files/CodeViewer";
import { FolderTree } from "lucide-react";

interface FilesViewProps {
  initialFilePath?: string | null;
  targetLine?: number | null;
  onAskAboutFile: (filePath: string) => void;
}

export function FilesView({
  initialFilePath,
  targetLine: externalTargetLine,
  onAskAboutFile,
}: FilesViewProps) {
  const {
    tree,
    selectedFilePath,
    fileContent,
    expandedFolders,
    toggleFolder,
    selectFile,
    fileSearch,
    setFileSearch,
    targetLine,
    totalFileCount,
    isLoadingContent,
    error,
  } = useFiles(initialFilePath);

  return (
    <section className="page-container files-view-wrapper">
      <div className="files-view-header">
        <div>
          <p className="eyebrow">Repository Files</p>
          <h1 className="view-title">Codebase Explorer &amp; Vector Chunks</h1>
          <p className="view-subtext">
            Browse files across directories and inspect how source code has been chunked and indexed into ChromaDB.
          </p>
        </div>

        <div className="files-stats-badge">
          <FolderTree className="w-4 h-4 text-accent" />
          <span>{totalFileCount} Indexed Files</span>
        </div>
      </div>

      {error && (
        <div className="error-message" role="alert">
          <p>{error}</p>
        </div>
      )}

      <div className="files-split-pane">
        {/* Left Tree Explorer */}
        <div className="files-tree-pane">
          <div className="pane-header-compact">
            <span className="pane-label">WORKSPACE EXPLORER</span>
          </div>
          <FileTree
            tree={tree}
            selectedFilePath={selectedFilePath}
            expandedFolders={expandedFolders}
            searchQuery={fileSearch}
            onSearchChange={setFileSearch}
            onToggleFolder={toggleFolder}
            onSelectFile={(path) => selectFile(path)}
          />
        </div>

        {/* Right Code Viewer */}
        <div className="files-code-pane">
          <CodeViewer
            fileData={fileContent}
            targetLine={externalTargetLine ?? targetLine}
            isLoading={isLoadingContent}
            onAskAboutFile={onAskAboutFile}
          />
        </div>
      </div>
    </section>
  );
}
