"use client";

import { useEffect, useRef, useState, useMemo } from "react";
import {
  Check,
  Copy,
  FileCode,
  Layers,
  MessageSquareCode,
} from "lucide-react";
import type { FileContentResponse } from "@/types/files";

interface CodeViewerProps {
  fileData: FileContentResponse | null;
  targetLine?: number | null;
  isLoading: boolean;
  onAskAboutFile: (filePath: string) => void;
}

export function CodeViewer({
  fileData,
  targetLine,
  isLoading,
  onAskAboutFile,
}: CodeViewerProps) {
  const [copied, setCopied] = useState(false);
  const [activeChunkIndex, setActiveChunkIndex] = useState<number | null>(null);
  const codeLinesRef = useRef<Record<number, HTMLDivElement | null>>({});

  const lines = useMemo(() => {
    if (!fileData) return [];
    return fileData.content.split("\n");
  }, [fileData]);

  // Scroll to target line if provided
  useEffect(() => {
    if (targetLine && codeLinesRef.current[targetLine]) {
      codeLinesRef.current[targetLine]?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [targetLine, fileData]);

  const handleCopy = async () => {
    if (!fileData) return;
    try {
      await navigator.clipboard.writeText(fileData.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy code:", err);
    }
  };

  const jumpToChunk = (startLine: number, idx: number) => {
    setActiveChunkIndex(idx);
    if (codeLinesRef.current[startLine]) {
      codeLinesRef.current[startLine]?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  };

  if (isLoading) {
    return (
      <div className="code-viewer-empty-state">
        <div className="spinner mb-3" />
        <p>Loading file content...</p>
      </div>
    );
  }

  if (!fileData) {
    return (
      <div className="code-viewer-empty-state">
        <FileCode className="w-12 h-12 text-muted opacity-40 mb-3" />
        <h3>Select a File</h3>
        <p>Choose any source file from the explorer tree to view its indexed code and chunks.</p>
      </div>
    );
  }

  const breadcrumbs = fileData.path.split("/");
  const fileSizeKb = (fileData.size / 1024).toFixed(1);

  return (
    <div className="code-viewer-container">
      {/* Top Bar */}
      <div className="code-viewer-header">
        <div className="code-breadcrumbs">
          {breadcrumbs.map((part, index) => (
            <span key={`${part}-${index}`} className="breadcrumb-segment">
              {index > 0 && <span className="breadcrumb-slash">/</span>}
              <span className={index === breadcrumbs.length - 1 ? "is-active-file" : ""}>
                {part}
              </span>
            </span>
          ))}
        </div>

        <div className="code-header-actions">
          <span className="file-meta-tag">{fileData.line_count} lines</span>
          <span className="file-meta-tag">{fileSizeKb} KB</span>
          {fileData.chunks.length > 0 && (
            <span className="file-meta-tag chunk-count-tag">
              <Layers className="w-3 h-3 mr-1 inline" />
              {fileData.chunks.length} chunks indexed
            </span>
          )}

          <button
            type="button"
            className="btn-code-action"
            onClick={handleCopy}
            title="Copy entire file contents"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-500" />
                <span>Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>

          <button
            type="button"
            className="btn-code-action-primary"
            onClick={() => onAskAboutFile(fileData.path)}
            title="Ask CodeLens AI about this file"
          >
            <MessageSquareCode className="w-3.5 h-3.5" />
            <span>Ask CodeLens</span>
          </button>
        </div>
      </div>

      {/* Chunks Ribbon */}
      {fileData.chunks.length > 0 && (
        <div className="chunks-ribbon">
          <span className="chunks-ribbon-label">Indexed Vector Chunks:</span>
          <div className="chunks-pills-list">
            {fileData.chunks.map((chunk, idx) => (
              <button
                key={`chunk-${chunk.start_line}-${idx}`}
                type="button"
                className={`chunk-pill ${activeChunkIndex === idx ? "is-active" : ""}`}
                onClick={() => jumpToChunk(chunk.start_line, idx)}
              >
                Chunk {idx + 1}: L{chunk.start_line}&ndash;{chunk.end_line}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Code Editor Body */}
      <div className="code-editor-body">
        <div className="code-line-numbers" aria-hidden="true">
          {lines.map((_, i) => {
            const lineNum = i + 1;
            const isTarget = targetLine === lineNum;
            return (
              <span
                key={lineNum}
                className={`line-num ${isTarget ? "is-target-line" : ""}`}
              >
                {lineNum}
              </span>
            );
          })}
        </div>

        <div className="code-text-area">
          <pre className="code-pre">
            <code>
              {lines.map((lineContent, i) => {
                const lineNum = i + 1;
                const isTarget = targetLine === lineNum;
                const inActiveChunk =
                  activeChunkIndex !== null &&
                  fileData.chunks[activeChunkIndex] &&
                  lineNum >= fileData.chunks[activeChunkIndex].start_line &&
                  lineNum <= fileData.chunks[activeChunkIndex].end_line;

                return (
                  <div
                    key={lineNum}
                    ref={(el) => {
                      codeLinesRef.current[lineNum] = el;
                    }}
                    className={`code-line-row ${
                      isTarget ? "is-target-line-row" : inActiveChunk ? "is-chunk-row" : ""
                    }`}
                  >
                    <span className="code-line-text">{lineContent || " "}</span>
                  </div>
                );
              })}
            </code>
          </pre>
        </div>
      </div>
    </div>
  );
}
