"use client";

import {
  FolderTree,
  GitFork,
  LayoutDashboard,
  MessageSquareCode,
  ShieldCheck,
} from "lucide-react";
import type { WorkspaceView } from "@/types/ui";

interface SidebarProps {
  activeView: WorkspaceView;
  onViewChange: (view: WorkspaceView) => void;
}

const navigation = [
  {
    id: "overview" as WorkspaceView,
    label: "Overview",
    icon: LayoutDashboard,
    badge: null,
  },
  {
    id: "chat" as WorkspaceView,
    label: "Code Chat",
    icon: MessageSquareCode,
    badge: "AI RAG",
  },
  {
    id: "architecture" as WorkspaceView,
    label: "Architecture",
    icon: GitFork,
    badge: "Flows",
  },
  {
    id: "files" as WorkspaceView,
    label: "File Explorer",
    icon: FolderTree,
    badge: null,
  },
];

export function Sidebar({ activeView, onViewChange }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header-label">WORKSPACE</div>
      <nav className="sidebar-nav" aria-label="Workspace navigation">
        {navigation.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item ${isActive ? "is-active" : ""}`}
              type="button"
              aria-current={isActive ? "page" : undefined}
              onClick={() => onViewChange(item.id)}
            >
              <span className="nav-icon-wrapper">
                <Icon className="w-4 h-4" />
              </span>
              <span className="nav-label">{item.label}</span>
              {item.badge && (
                <span className={`nav-badge ${isActive ? "badge-active" : ""}`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-context-box">
          <div className="context-box-top">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
            <strong className="text-xs">Context Engine Active</strong>
          </div>
          <p className="text-muted text-xs mt-1">
            Chroma vector store &amp; AST analyzer grounded to local repository.
          </p>
        </div>
      </div>
    </aside>
  );
}
