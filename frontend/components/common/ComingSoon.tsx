import type { WorkspaceView } from "@/types/ui";

interface ComingSoonProps {
  section: WorkspaceView;
}

const labels: Record<WorkspaceView, string> = {
  overview: "Overview",
  chat: "Chat",
  architecture: "Architecture",
  files: "Files",
};

export function ComingSoon({ section }: ComingSoonProps) {
  return (
    <section
      className="page-container coming-soon"
      aria-labelledby="coming-soon-title"
    >
      <div className="empty-state">
        <span className="empty-symbol" aria-hidden="true">⌘</span>
        <h1 id="coming-soon-title">{labels[section]}</h1>
        <p>
          This workspace area is not part of the current release. Your
          repository is ready to explore in chat.
        </p>
        <span className="coming-soon-label">Coming soon</span>
      </div>
    </section>
  );
}
