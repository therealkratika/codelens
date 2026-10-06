"use client";

import { ExternalLink, FileCode } from "lucide-react";
import { formatSourceLines } from "@/lib/utils/formatSource";
import type { SourceReference } from "@/types/chat";

interface SourceListProps {
  sources: SourceReference[];
  onOpenFile?: (file: string, line?: number) => void;
}

export function SourceList({ sources, onOpenFile }: SourceListProps) {
  if (sources.length === 0) {
    return <p className="stat-label">No source references were returned.</p>;
  }

  return (
    <div className="source-list">
      {sources.map((source, index) => {
        const line = source.start_line ?? undefined;
        return (
          <div
            className="source-item"
            key={`${source.file}:${source.start_line ?? "unknown"}:${index}`}
          >
            <div className="source-file-wrapper">
              <FileCode className="w-3.5 h-3.5 text-accent flex-shrink-0" />
              {onOpenFile ? (
                <button
                  type="button"
                  className="source-file-link"
                  onClick={() => onOpenFile(source.file, line)}
                  title={`Open ${source.file}${line ? ` at line ${line}` : ""}`}
                >
                  <span className="source-file">{source.file}</span>
                  <ExternalLink className="w-3 h-3 ml-1 text-muted" />
                </button>
              ) : (
                <span className="source-file" title={source.file}>
                  {source.file}
                </span>
              )}
            </div>

            <span className="source-detail">
              {formatSourceLines(source)}
              {typeof source.score === "number" ? (
                <span className="source-score" title="Retrieval relevance score">
                  {source.score.toFixed(2)}
                </span>
              ) : null}
            </span>
          </div>
        );
      })}
    </div>
  );
}
