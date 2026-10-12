import SourceReferences from "../chat/SourceReferences";

function InlineText({ children }) {
  const parts = String(children).split(/(`[^`]+`|\*\*[^*]+\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code className="answer-inline-code" key={index}>
          {part.slice(1, -1)}
        </code>
      );
    }
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    return <span key={index}>{part}</span>;
  });
}

export default function AssistantResponse({ content, sources = [] }) {
  const text =
    typeof content === "string" ? content : JSON.stringify(content, null, 2);
  const lines = text.replace(/\r\n/g, "\n").split("\n");
  const blocks = [];
  let paragraph = [];
  let code = null;

  function flushParagraph() {
    if (paragraph.length) {
      blocks.push({ type: "paragraph", text: paragraph.join(" ") });
      paragraph = [];
    }
  }

  lines.forEach((line) => {
    if (line.trim().startsWith("```")) {
      flushParagraph();
      if (code) {
        blocks.push({
          type: "code",
          language: code.language,
          text: code.lines.join("\n"),
        });
        code = null;
      } else {
        code = { language: line.trim().slice(3).trim(), lines: [] };
      }
      return;
    }
    if (code) {
      code.lines.push(line);
      return;
    }
    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      return;
    }
    const heading = trimmed.match(/^#{1,4}\s+(.+)$/);
    if (heading) {
      flushParagraph();
      blocks.push({ type: "heading", text: heading[1].replace(/\*+/g, "") });
      return;
    }
    const bullet = trimmed.match(/^[-*]\s+(.+)$/);
    if (bullet) {
      flushParagraph();
      const previous = blocks[blocks.length - 1];
      if (previous?.type === "list") previous.items.push(bullet[1]);
      else blocks.push({ type: "list", ordered: false, items: [bullet[1]] });
      return;
    }
    const ordered = trimmed.match(/^\d+[.)]\s+(.+)$/);
    if (ordered) {
      flushParagraph();
      const previous = blocks[blocks.length - 1];
      if (previous?.type === "list" && previous.ordered)
        previous.items.push(ordered[1]);
      else blocks.push({ type: "list", ordered: true, items: [ordered[1]] });
      return;
    }
    paragraph.push(trimmed);
  });

  if (code)
    blocks.push({
      type: "code",
      language: code.language,
      text: code.lines.join("\n"),
    });
  flushParagraph();

  return (
    <div className="assistant-response">
      {blocks.map((block, index) => {
        if (block.type === "heading")
          return (
            <h3 key={index}>
              <InlineText>{block.text}</InlineText>
            </h3>
          );
        if (block.type === "code")
          return (
            <pre className="answer-code" key={index}>
              {block.language && (
                <span className="answer-code-language">{block.language}</span>
              )}
              <code>{block.text}</code>
            </pre>
          );
        if (block.type === "list") {
          const List = block.ordered ? "ol" : "ul";
          return (
            <List className="answer-list" key={index}>
              {block.items.map((item, itemIndex) => (
                <li key={itemIndex}>
                  <InlineText>{item}</InlineText>
                </li>
              ))}
            </List>
          );
        }
        return (
          <p key={index}>
            <InlineText>{block.text}</InlineText>
          </p>
        );
      })}
      <SourceReferences sources={sources} />
    </div>
  );
}
