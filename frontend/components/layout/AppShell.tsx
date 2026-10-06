"use client";

import type { ReactNode } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import type { WorkspaceView } from "@/types/ui";

interface AppShellProps {
  activeView: WorkspaceView;
  isLoaded: boolean;
  repositoryName?: string;
  onViewChange: (view: WorkspaceView) => void;
  onSwitchRepository?: () => void;
  children: ReactNode;
}

export function AppShell({
  activeView,
  isLoaded,
  repositoryName,
  onViewChange,
  onSwitchRepository,
  children,
}: AppShellProps) {
  return (
    <div className="app-frame">
      <TopBar
        isLoaded={isLoaded}
        repositoryName={repositoryName}
        onSwitchRepository={onSwitchRepository}
      />
      {isLoaded ? (
        <div className="workspace">
          <Sidebar activeView={activeView} onViewChange={onViewChange} />
          <main className="main-content">{children}</main>
        </div>
      ) : (
        children
      )}
    </div>
  );
}
