"use client";

import Link from "next/link";
import { FolderGit2, RefreshCw, Sparkles } from "lucide-react";

interface TopBarProps {
  isLoaded: boolean;
  repositoryName?: string;
  onSwitchRepository?: () => void;
}

export function TopBar({
  isLoaded,
  repositoryName,
  onSwitchRepository,
}: TopBarProps) {
  return (
    <header className="topbar">
      <Link className="brand-lockup" href="/" aria-label="CodeLens home">
        <span className="brand-mark" aria-hidden="true">
          <Sparkles className="w-4 h-4 text-white" />
        </span>
        <span className="brand-title">CodeLens</span>
        <span className="brand-subtitle">AI Codebase Intelligence</span>
      </Link>

      <div className="topbar-meta">
        {isLoaded && repositoryName ? (
          <div className="repository-chip" title={`Active repository: ${repositoryName}`}>
            <FolderGit2 className="w-3.5 h-3.5 text-accent" />
            <span className="repo-name">{repositoryName}</span>
          </div>
        ) : null}

        <div className={`status-indicator ${isLoaded ? "is-connected" : ""}`}>
          <span className="status-dot-pulse" aria-hidden="true" />
          <span>{isLoaded ? "Repository indexed" : "No repository active"}</span>
        </div>

        {isLoaded && onSwitchRepository && (
          <button
            type="button"
            className="btn-topbar-action"
            onClick={onSwitchRepository}
            title="Import or switch another repository"
          >
            <RefreshCw className="w-3 h-3" />
            <span>Switch Repo</span>
          </button>
        )}
      </div>
    </header>
  );
}
