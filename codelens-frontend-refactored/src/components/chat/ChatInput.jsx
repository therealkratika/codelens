import { useState } from "react";
export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState("");
  function submit(e) { e.preventDefault(); if (value.trim() && !disabled) { onSend(value.trim()); setValue(""); } }
  return <form className="chat-composer" onSubmit={submit}><textarea value={value} onChange={e=>setValue(e.target.value)} placeholder={disabled ? "Activate a repository to start chatting…" : "Ask anything about your codebase…"} disabled={disabled} rows={2} onKeyDown={e=>{if(e.key==="Enter"&&!e.shiftKey){e.preventDefault();submit(e);}}}/><button className="send-button" disabled={disabled || !value.trim()} aria-label="Send message">↑</button><div className="composer-hint">AI can make mistakes. Verify important details.<span>Enter to send · Shift + Enter for new line</span></div></form>;
}
