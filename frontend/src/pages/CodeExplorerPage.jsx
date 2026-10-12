import { useEffect, useMemo, useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import Button from "../components/common/Button";
import { useRepository } from "../context/RepositoryContext";
import { askCodebase } from "../api/chatApi";
import { getFileContent, getFileTree } from "../api/filesApi";
import EmptyState from "../components/common/EmptyState";
import AssistantResponse from "../components/common/AssistantResponse";

function flattenFiles(nodes, result = []) {
  nodes.forEach((node) => {
    if (node.type === "file") result.push(node);
    if (node.children) flattenFiles(node.children, result);
  });
  return result;
}

function FileTree({ nodes, selectedPath, onSelect, filter }) {
  return (
    <ul className="file-tree">
      {nodes.map((node) => {
        if (node.name === ".DS_Store") return null;
        const matches =
          node.name.toLowerCase().includes(filter.toLowerCase()) ||
          node.path.toLowerCase().includes(filter.toLowerCase());
        const visibleChildren =
          node.children?.filter(
            (child) =>
              child.type === "directory" ||
              child.name.toLowerCase().includes(filter.toLowerCase()) ||
              child.path.toLowerCase().includes(filter.toLowerCase()),
          ) || [];
        if (
          filter &&
          node.type === "directory" &&
          !matches &&
          !visibleChildren.length
        )
          return null;
        return (
          <li key={node.path || node.name}>
            {node.type === "directory" ? (
              <details open={Boolean(filter)}>
                <summary>
                  <span className="tree-chevron">›</span>
                  <span className="tree-folder">⌁</span>
                  {node.name}
                </summary>
                <FileTree
                  nodes={node.children || []}
                  selectedPath={selectedPath}
                  onSelect={onSelect}
                  filter={filter}
                />
              </details>
            ) : (
              <button
                className={`tree-file ${selectedPath === node.path ? "selected" : ""}`}
                onClick={() => onSelect(node.path)}
                title={node.path}
              >
                <span className="tree-file-icon">{node.extension || "·"}</span>
                <span>{node.name}</span>
                {node.chunk_count ? <small>{node.chunk_count}</small> : null}
              </button>
            )}
          </li>
        );
      })}
    </ul>
  );
}

export default function CodeExplorerPage() {
  const { activeRepository, goToImport } = useRepository();
  const [tree, setTree] = useState([]);
  const [treeFilter, setTreeFilter] = useState("");
  const [selectedPath, setSelectedPath] = useState("");
  const [file, setFile] = useState(null);
  const [treeBusy, setTreeBusy] = useState(false);
  const [fileBusy, setFileBusy] = useState(false);
  const [error, setError] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [chatBusy, setChatBusy] = useState(false);
  const files = useMemo(() => flattenFiles(tree), [tree]);

  useEffect(() => {
    if (!activeRepository) return;
    setTreeBusy(true);
    setError("");
    getFileTree()
      .then((result) => setTree(result.tree || []))
      .catch((err) =>
        setError(err.message || "Could not load the repository files."),
      )
      .finally(() => setTreeBusy(false));
  }, [activeRepository?.repository_path]);

  async function selectFile(path) {
    setSelectedPath(path);
    setFileBusy(true);
    setError("");
    try {
      setFile(await getFileContent(path));
    } catch (err) {
      setError(err.message || "Could not open this file.");
    } finally {
      setFileBusy(false);
    }
  }

  async function askAboutFile(event) {
    event.preventDefault();
    if (!question.trim() || !file || chatBusy) return;
    setChatBusy(true);
    setError("");
    try {
      const result = await askCodebase(
        `In ${file.path}, answer this question using the repository context: ${question.trim()}. Cite relevant files and line ranges.`,
      );
      setAnswer(result);
      setQuestion("");
    } catch (err) {
      setError(err.message || "Could not ask about this file.");
    } finally {
      setChatBusy(false);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="SOURCE CONTEXT"
        title="Code explorer"
        description="Browse the active repository, open a file, and ask questions about the code in context."
      />
      {!activeRepository ? (
        <EmptyState
          title="No active repository"
          description="Import and activate a repository to explore its source."
          action={<Button onClick={goToImport}>Import repository</Button>}
        />
      ) : (
        <section className="explorer-workspace card">
          <aside className="explorer-sidebar">
            <div className="explorer-sidebar-heading">
              <div>
                <span className="eyebrow">FILES</span>
                <strong>{files.length} source files</strong>
              </div>
              <button
                className="icon-button"
                onClick={() => setTreeFilter("")}
                title="Clear file filter"
              >
                ↺
              </button>
            </div>
            <input
              className="file-filter"
              value={treeFilter}
              onChange={(event) => setTreeFilter(event.target.value)}
              placeholder="Filter files…"
            />
            <div className="tree-scroll">
              {treeBusy ? (
                <div className="explorer-placeholder">
                  Loading repository tree…
                </div>
              ) : (
                <FileTree
                  nodes={tree}
                  selectedPath={selectedPath}
                  onSelect={selectFile}
                  filter={treeFilter}
                />
              )}
            </div>
          </aside>
          <div className="explorer-main">
            {error && (
              <div className="alert alert-error" role="alert">
                {error}
              </div>
            )}
            {!file && !fileBusy ? (
              <div className="explorer-welcome">
                <div className="explorer-welcome-icon">&lt;/&gt;</div>
                <h2>Open a file to start exploring</h2>
                <p>
                  Choose a file from the tree to inspect its source and ask
                  CodeLens about the implementation.
                </p>
              </div>
            ) : fileBusy ? (
              <div className="explorer-placeholder">
                Opening {selectedPath}…
              </div>
            ) : (
              <>
                <div className="code-viewer-header">
                  <div>
                    <span className="eyebrow">OPEN FILE</span>
                    <strong>{file.path}</strong>
                  </div>
                  <span className="file-meta">
                    {file.line_count} lines · {file.chunks?.length || 0} indexed
                    chunks
                  </span>
                </div>
                <div className="code-viewer">
                  {file.content.split("\n").map((line, index) => (
                    <div className="code-line" key={index}>
                      <span>{index + 1}</span>
                      <code>{line || " "}</code>
                    </div>
                  ))}
                </div>
                <div className="file-chat">
                  <div className="file-chat-heading">
                    <span>✳</span>
                    <div>
                      <strong>Ask about this file</strong>
                      <small>Answers are grounded in {file.path}</small>
                    </div>
                  </div>
                  <form onSubmit={askAboutFile} className="file-chat-form">
                    <input
                      value={question}
                      onChange={(event) => setQuestion(event.target.value)}
                      placeholder="What does this file do? How is this function used?"
                      disabled={chatBusy}
                    />
                    <Button
                      type="submit"
                      disabled={chatBusy || !question.trim()}
                    >
                      {chatBusy ? "Thinking…" : "Ask AI"}
                    </Button>
                  </form>
                  {answer && (
                    <div className="file-chat-answer">
                      <AssistantResponse
                        content={answer.answer || answer.response || answer}
                        sources={answer.sources}
                      />
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </section>
      )}
    </>
  );
}
