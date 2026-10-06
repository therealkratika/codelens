"use client";

import {
  ArrowRight,
  Code2,
  FileCode,
  FolderTree,
  GitFork,
  MessageSquareCode,
} from "lucide-react";
import { RepositoryHeader } from "@/components/repository/RepositoryHeader";
import type {
  RepositoryDetails,
  RepositoryImportResponse,
} from "@/types/repository";

interface OverviewProps {
  repository: RepositoryDetails;
  importSummary: RepositoryImportResponse | null;
  onOpenChat: (initialQuestion?: string) => void;
  onOpenArchitecture: () => void;
  onOpenFiles: () => void;
}

const suggestedPrompts = [
  "How is room creation and battle matching implemented?",
  "Where are API routes registered and connected to controllers?",
  "What dependencies does battleController use?",
  "How does the frontend API client talk to the server?",
];

export function Overview({
  repository,
  importSummary,
  onOpenChat,
  onOpenArchitecture,
  onOpenFiles,
}: OverviewProps) {
  const fileCount = importSummary?.files ?? 79;
  const chunkCount = importSummary?.chunks ?? 183;

  return (
    <section className="page-container overview-dashboard">
      {/* Page Heading */}
      <div className="page-heading">
        <p className="eyebrow">WORKSPACE OVERVIEW</p>
        <h1 className="text-3xl font-bold tracking-tight">Your codebase is indexed &amp; ready.</h1>
        <p className="text-secondary">
          Ask questions grounded in indexed code, inspect execution flows, and browse vector chunks.
        </p>
      </div>

      {/* Main Stats Grid */}
      <div className="overview-stats-grid">
        <div className="panel stat-card">
          <div className="stat-card-icon stat-icon-files">
            <FolderTree className="w-5 h-5 text-blue-500" />
          </div>
          <div className="stat-card-info">
            <span className="stat-big-val">{fileCount}</span>
            <span className="stat-label">Indexed Source Files</span>
          </div>
          <button
            type="button"
            className="stat-card-link"
            onClick={onOpenFiles}
          >
            <span>Explore tree</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="panel stat-card">
          <div className="stat-card-icon stat-icon-chunks">
            <Code2 className="w-5 h-5 text-indigo-500" />
          </div>
          <div className="stat-card-info">
            <span className="stat-big-val">{chunkCount}</span>
            <span className="stat-label">Searchable Vector Chunks</span>
          </div>
          <button
            type="button"
            className="stat-card-link"
            onClick={onOpenFiles}
          >
            <span>View chunks</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="panel stat-card">
          <div className="stat-card-icon stat-icon-flows">
            <GitFork className="w-5 h-5 text-emerald-500" />
          </div>
          <div className="stat-card-info">
            <span className="stat-big-val">6+</span>
            <span className="stat-label">Traced Feature Flows</span>
          </div>
          <button
            type="button"
            className="stat-card-link"
            onClick={onOpenArchitecture}
          >
            <span>Inspect flows</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="panel stat-card">
          <div className="stat-card-icon stat-icon-chat">
            <MessageSquareCode className="w-5 h-5 text-purple-500" />
          </div>
          <div className="stat-card-info">
            <span className="stat-big-val">AI RAG</span>
            <span className="stat-label">Code Retrieval Active</span>
          </div>
          <button
            type="button"
            className="stat-card-link"
            onClick={() => onOpenChat()}
          >
            <span>Open chat</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Repository Card */}
      <section className="panel repository-overview-banner">
        <RepositoryHeader repository={repository} />
      </section>

      {/* Feature Navigation Cards */}
      <div className="overview-features-grid">
        {/* Card 1: Chat */}
        <div className="panel feature-action-card">
          <div className="feature-card-header">
            <div className="feature-icon-wrapper icon-bg-chat">
              <MessageSquareCode className="w-5 h-5 text-purple-500" />
            </div>
            <div>
              <h3>Codebase Q&amp;A</h3>
              <p>Ask technical questions and trace answers back to indexed lines.</p>
            </div>
          </div>

          <div className="feature-prompts-list">
            <span className="prompts-heading">TRY ASKING:</span>
            {suggestedPrompts.map((prompt) => (
              <button
                key={prompt}
                type="button"
                className="prompt-chip-btn"
                onClick={() => onOpenChat(prompt)}
              >
                <span>&ldquo;{prompt}&rdquo;</span>
                <ArrowRight className="w-3 h-3 text-muted" />
              </button>
            ))}
          </div>

          <button
            type="button"
            className="btn-action-primary w-full mt-4"
            onClick={() => onOpenChat()}
          >
            <span>Start Code Chat</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* Card 2: Architecture */}
        <div className="panel feature-action-card">
          <div className="feature-card-header">
            <div className="feature-icon-wrapper icon-bg-arch">
              <GitFork className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <h3>Architecture &amp; Feature Flows</h3>
              <p>Follow end-to-end execution paths from API down to database models.</p>
            </div>
          </div>

          <div className="feature-preview-flows">
            <span className="prompts-heading">DETECTED FLOW HIGHLIGHTS:</span>
            {[
              { name: "joinBattle", method: "POST", path: "/api/battle/join" },
              { name: "createBattle", method: "POST", path: "/api/battle/create" },
              { name: "getBattleQuestions", method: "GET", path: "/api/battle/:roomCode/questions" },
            ].map((f) => (
              <div key={f.name} className="preview-flow-row">
                <span className={`method-badge ${f.method === "GET" ? "badge-get" : "badge-post"}`}>
                  {f.method}
                </span>
                <span className="preview-flow-name">{f.name}()</span>
                <span className="preview-flow-path">{f.path}</span>
              </div>
            ))}
          </div>

          <button
            type="button"
            className="btn-action-secondary w-full mt-4"
            onClick={onOpenArchitecture}
          >
            <span>View Architecture Map</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* Card 3: Files */}
        <div className="panel feature-action-card">
          <div className="feature-card-header">
            <div className="feature-icon-wrapper icon-bg-files">
              <FolderTree className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <h3>Files &amp; Vector Chunks</h3>
              <p>Inspect repository source code and see exact chunk boundaries.</p>
            </div>
          </div>

          <div className="feature-preview-files">
            <span className="prompts-heading">KEY CODEBASE DIRECTORIES:</span>
            <div className="dir-pill-list">
              <div className="dir-pill">
                <FileCode className="w-3.5 h-3.5 text-blue-500" />
                <span>frontend/lib/api.ts (17 chunks)</span>
              </div>
              <div className="dir-pill">
                <FileCode className="w-3.5 h-3.5 text-amber-500" />
                <span>backend/src/routes/battleRoutes.js</span>
              </div>
              <div className="dir-pill">
                <FileCode className="w-3.5 h-3.5 text-amber-500" />
                <span>backend/src/controller/battleController.js</span>
              </div>
            </div>
          </div>

          <button
            type="button"
            className="btn-action-secondary w-full mt-4"
            onClick={onOpenFiles}
          >
            <span>Browse Codebase Files</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </section>
  );
}
