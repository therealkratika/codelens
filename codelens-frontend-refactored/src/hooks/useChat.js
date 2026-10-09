import { useState } from "react";
import { askCodebase } from "../api/chatApi";
export default function useChat() {
  const [messages, setMessages] = useState([]); const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  async function send(question) {
    setError(""); setMessages(old => [...old, { role: "user", content: question }]); setBusy(true);
    try { const result = await askCodebase(question); setMessages(old => [...old, { role: "assistant", content: result.answer || result.response || "The backend returned no answer.", sources: result.sources || [] }]); }
    catch (e) { setError(e.message || "Chat request failed."); }
    finally { setBusy(false); }
  }
  return { messages, busy, error, setError, send };
}
