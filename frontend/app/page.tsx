"use client";

import { useState, useCallback, useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { Overview } from "@/components/repository/Overview";
import { ArchitectureView } from "@/components/architecture/ArchitectureView";
import { FilesView } from "@/components/files/FilesView";
import { RepositoryImport } from "@/components/repository/RepositoryImport";
import { useChat } from "@/hooks/useChat";
import { useRepository } from "@/hooks/useRepository";
import { getRepositorySuggestions } from "@/lib/api/repository";
import type { WorkspaceView } from "@/types/ui";
import type { FeatureFlow } from "@/types/architecture";

export default function Home() {
  const repositoryState = useRepository();
  const chat = useChat();
  const [activeView, setActiveView] = useState<WorkspaceView>("overview");
  const [showImportModal, setShowImportModal] = useState(false);
  const [suggestionData, setSuggestionData] = useState<{
    repositoryPath: string;
    suggestions: string[];
    error: string | null;
  } | null>(null);

  // Cross-view navigation state
  const [prefilledChatQuestion, setPrefilledChatQuestion] = useState<string>("");
  const [targetFileForViewer, setTargetFileForViewer] = useState<string | null>(null);
  const [targetLineForViewer, setTargetLineForViewer] = useState<number | null>(null);

  const repository = repositoryState.repository;
  const isLoaded = repository !== null && !showImportModal;
  const repositoryPath = repository?.repository_path;
  const repositoryName = repository?.repository;
  const clearChat = chat.clearChat;

  useEffect(() => {
    let cancelled = false;

    if (!repositoryPath || !repositoryName) {
      return () => {
        cancelled = true;
      };
    }

    getRepositorySuggestions()
      .then((result) => {
        if (!cancelled && result.repository === repositoryName) {
          setSuggestionData({
            repositoryPath,
            suggestions: result.suggestions,
            error: null,
          });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setSuggestionData({
            repositoryPath,
            suggestions: [],
            error: "Could not load suggested questions for this repository.",
          });
        }
      });

    return () => {
      cancelled = true;
    };
  }, [repositoryPath, repositoryName]);

  const repositorySuggestions =
    repositoryPath && suggestionData?.repositoryPath === repositoryPath
      ? suggestionData.suggestions
      : [];
  const suggestionError =
    repositoryPath && suggestionData?.repositoryPath === repositoryPath
      ? suggestionData.error
      : null;

  const handleOpenChatWithQuestion = useCallback((question?: string) => {
    if (question) {
      setPrefilledChatQuestion(question);
    }
    setActiveView("chat");
  }, []);

  const handleAskAboutFlow = useCallback((flow: FeatureFlow) => {
    const question = `Explain the complete execution flow for ${flow.name}() from frontend down to the database models.`;
    setPrefilledChatQuestion(question);
    setActiveView("chat");
  }, []);

  const handleAskAboutFile = useCallback((filePath: string) => {
    const question = `Explain the implementation, dependencies, and main responsibilities of ${filePath}.`;
    setPrefilledChatQuestion(question);
    setActiveView("chat");
  }, []);

  const handleOpenFile = useCallback((file: string, line?: number) => {
    setTargetFileForViewer(file);
    setTargetLineForViewer(line ?? null);
    setActiveView("files");
  }, []);

  const handleSwitchRepository = useCallback(() => {
    setShowImportModal(true);
  }, []);

  const handleCompletedImport = useCallback(
    async (repoUrl: string) => {
      const imported = await repositoryState.importRepository(repoUrl);
      if (imported) {
        clearChat();
        setPrefilledChatQuestion("");
        setShowImportModal(false);
        setActiveView("overview");
      }
      return imported;
    },
    [repositoryState, clearChat],
  );

  const handleActivateRepository = useCallback(
    async (repositoryPath: string) => {
      const activated = await repositoryState.activateRepository(repositoryPath);
      if (activated) {
        clearChat();
        setPrefilledChatQuestion("");
        setShowImportModal(false);
        setActiveView("overview");
      }
      return activated;
    },
    [repositoryState, clearChat],
  );

  return (
    <AppShell
      activeView={activeView}
      isLoaded={isLoaded}
      repositoryName={repository?.repository}
      onViewChange={setActiveView}
      onSwitchRepository={handleSwitchRepository}
    >
      {repositoryState.isChecking ? (
        <main className="startup-state" aria-live="polite">
          <div className="startup-spinner-box">
            <span className="brand-mark animate-pulse" aria-hidden="true">C</span>
            <p>Connecting to CodeLens Intelligence Engine...</p>
          </div>
        </main>
      ) : !repository || showImportModal ? (
        <div className="relative">
          {showImportModal && repository && (
            <div className="import-modal-banner">
              <span>Currently loaded: <strong>{repository.repository}</strong></span>
              <button
                type="button"
                className="btn-cancel-switch"
                onClick={() => setShowImportModal(false)}
              >
                Cancel
              </button>
            </div>
          )}
          <RepositoryImport
            isImporting={repositoryState.isImporting}
            isActivating={repositoryState.isActivating}
            error={repositoryState.error}
            statusError={repositoryState.statusError}
            savedRepositories={repositoryState.savedRepositories}
            activeRepositoryPath={
              repository?.repository_path ??
              repositoryState.savedRepositories.find(
                (saved) => saved.repository === repository?.repository,
              )?.repository_path ??
              null
            }
            onImport={handleCompletedImport}
            onActivate={handleActivateRepository}
          />
        </div>
      ) : activeView === "chat" ? (
        <ChatInterface
          messages={chat.messages}
          suggestions={repositorySuggestions}
          suggestionsError={suggestionError}
          isLoading={chat.isLoading}
          error={chat.error}
          prefilledQuestion={prefilledChatQuestion}
          onAsk={chat.ask}
          onClearError={chat.clearError}
          onClearChat={chat.clearChat}
          onOpenFile={handleOpenFile}
          onClearPrefill={() => setPrefilledChatQuestion("")}
        />
      ) : activeView === "overview" ? (
        <Overview
          repository={repository}
          importSummary={repositoryState.importSummary}
          suggestedPrompts={repositorySuggestions}
          suggestionsError={suggestionError}
          onOpenChat={handleOpenChatWithQuestion}
          onOpenArchitecture={() => setActiveView("architecture")}
          onOpenFiles={() => setActiveView("files")}
        />
      ) : activeView === "architecture" ? (
        <ArchitectureView
          onAskAboutFlow={handleAskAboutFlow}
          onOpenFile={handleOpenFile}
        />
      ) : activeView === "files" ? (
        <FilesView
          initialFilePath={targetFileForViewer}
          targetLine={targetLineForViewer}
          onAskAboutFile={handleAskAboutFile}
        />
      ) : (
        <Overview
          repository={repository}
          importSummary={repositoryState.importSummary}
          suggestedPrompts={repositorySuggestions}
          suggestionsError={suggestionError}
          onOpenChat={handleOpenChatWithQuestion}
          onOpenArchitecture={() => setActiveView("architecture")}
          onOpenFiles={() => setActiveView("files")}
        />
      )}
    </AppShell>
  );
}
