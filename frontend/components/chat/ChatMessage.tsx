"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { SourceList } from "@/components/chat/SourceList";
import { Spinner } from "@/components/common/Spinner";
import type { ChatMessage as ChatMessageData } from "@/types/ui";

interface ChatMessageProps {
  message: ChatMessageData;
  isLoading: boolean;
  onOpenFile?: (file: string, line?: number) => void;
}

function CodeBlock({ code, lang }: { code: string; lang: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="chat-code-block">
      <div className="chat-code-header">
        <span className="code-lang-tag">{lang || "code"}</span>
        <button
          type="button"
          className="btn-copy-code"
          onClick={handleCopy}
          title="Copy code"
        >
          {copied ? (
            <>
              <Check className="w-3 h-3 text-emerald-500" />
              <span>Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-3 h-3" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      <pre className="chat-code-pre">
        <code>{code}</code>
      </pre>
    </div>
  );
}

function renderFormattedAnswer(answer: string) {
  // Split by code blocks first: ```lang\ncode\n```
  const codeBlockRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = codeBlockRegex.exec(answer)) !== null) {
    if (match.index > lastIndex) {
      const textBefore = answer.slice(lastIndex, match.index);
      parts.push(renderTextWithInlineCode(textBefore, `text-${lastIndex}`));
    }
    const lang = match[1] || "";
    const code = match[2];
    parts.push(
      <CodeBlock key={`code-${match.index}`} code={code} lang={lang} />,
    );
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < answer.length) {
    parts.push(
      renderTextWithInlineCode(answer.slice(lastIndex), `text-${lastIndex}`),
    );
  }

  return parts;
}

function renderTextWithInlineCode(text: string, keyPrefix: string) {
  // Split paragraphs and lines
  const lines = text.split("\n");
  return (
    <div key={keyPrefix} className="answer-prose">
      {lines.map((line, lIdx) => {
        const trimmed = line.trim();
        if (!trimmed) {
          return <div key={`${keyPrefix}-blank-${lIdx}`} className="h-2" />;
        }

        // Bullet point
        const isBullet = trimmed.startsWith("- ") || trimmed.startsWith("* ");
        const content = isBullet ? trimmed.slice(2) : line;

        // Split by inline code: `code`
        const inlineCodeParts = content.split(/(`[^`]+`)/g);

        const renderedLine = inlineCodeParts.map((part, pIdx) => {
          if (part.startsWith("`") && part.endsWith("`")) {
            return (
              <code
                className="inline-code"
                key={`${keyPrefix}-${lIdx}-${pIdx}`}
              >
                {part.slice(1, -1)}
              </code>
            );
          }
          // Bold formatting **text**
          const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
          return boldParts.map((bPart, bIdx) => {
            if (bPart.startsWith("**") && bPart.endsWith("**")) {
              return (
                <strong key={`${keyPrefix}-${lIdx}-${pIdx}-${bIdx}`}>
                  {bPart.slice(2, -2)}
                </strong>
              );
            }
            return <span key={`${keyPrefix}-${lIdx}-${pIdx}-${bIdx}`}>{bPart}</span>;
          });
        });

        if (isBullet) {
          return (
            <div
              key={`${keyPrefix}-bullet-${lIdx}`}
              className="chat-bullet-row"
            >
              <span className="bullet-dot">&bull;</span>
              <span>{renderedLine}</span>
            </div>
          );
        }

        return (
          <p key={`${keyPrefix}-p-${lIdx}`} className="chat-paragraph">
            {renderedLine}
          </p>
        );
      })}
    </div>
  );
}

export function ChatMessage({
  message,
  isLoading,
  onOpenFile,
}: ChatMessageProps) {
  return (
    <article className="chat-message">
      <section className="message-section">
        <p className="message-label">QUESTION</p>
        <p className="question-text">{message.question}</p>
      </section>

      <section className="message-section">
        <div className="flex items-center gap-2 mb-2">
          <p className="message-label mb-0">CODELENS ANSWER</p>
          <span className="badge-grounded">Repository-grounded</span>
        </div>

        {message.answer ? (
          <div className="answer-text">
            {renderFormattedAnswer(message.answer)}
          </div>
        ) : isLoading ? (
          <div className="answer-loading" aria-live="polite">
            <Spinner />
            <span>Retrieving codebase context, tracing AST, and generating answer...</span>
          </div>
        ) : null}
      </section>

      {message.answer && message.sources && message.sources.length > 0 ? (
        <section className="message-section">
          <p className="message-label">GROUNDED SOURCES ({message.sources.length})</p>
          <SourceList sources={message.sources} onOpenFile={onOpenFile} />
        </section>
      ) : null}
    </article>
  );
}
