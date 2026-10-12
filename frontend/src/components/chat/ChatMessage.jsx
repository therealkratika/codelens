import AssistantResponse from "../common/AssistantResponse";
export default function ChatMessage({ message }) {
  const user = message.role === "user";
  return <div className={`message-row ${message.role}`}><div className={`message-avatar ${message.role}`}>{user ? "You" : "✳"}</div><div className="message-body"><span className="message-author">{user ? "You" : "CodeLens"}</span><div className="message-bubble">{user ? message.content : <AssistantResponse content={message.content} sources={message.sources}/>}</div>{user ? null : null}</div></div>;
}
