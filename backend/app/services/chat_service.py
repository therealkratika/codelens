import logging
from pathlib import Path

from fastapi import HTTPException

from app import chat_storage
from app.core.state import AppState
from app.repository_storage import get_saved_repositories, normalize_repo_url


logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, state: AppState):
        self.state = state

    def repository_identity(self):
        manager = self.state.repository_manager
        repository_path = manager.get_repository_path()
        if not repository_path:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No repository is currently active. "
                    "Import or activate a repository first."
                ),
            )

        repository_key = repository_path
        for saved in get_saved_repositories():
            saved_path = saved.get("repository_path")
            if (
                saved.get("repo_url")
                and saved_path
                and (
                    str(Path(saved_path).expanduser().resolve())
                    == str(Path(repository_path).expanduser().resolve())
                    or Path(saved_path).name == Path(repository_path).name
                )
            ):
                repository_key = saved.get("normalized_url") or normalize_repo_url(
                    saved["repo_url"]
                )
                break

        return (
            repository_key,
            manager.get_repository(),
            repository_path,
        )

    def create_session(self, title=None):
        key, repository, path = self.repository_identity()
        return chat_storage.create_chat_session(key, repository, path, title)

    def list_sessions(self):
        key, _, _ = self.repository_identity()
        return chat_storage.list_chat_sessions(key)

    def get_session(self, session_id):
        key, _, _ = self.repository_identity()
        session = chat_storage.get_chat_session(key, session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Chat session was not found.")
        return session

    def delete_session(self, session_id):
        key, _, _ = self.repository_identity()
        if not chat_storage.delete_chat_session(key, session_id):
            raise HTTPException(status_code=404, detail="Chat session was not found.")
        return {"deleted": True, "session_id": session_id}

    def rename_session(self, session_id, title):
        title = title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Chat name cannot be empty.")
        key, _, _ = self.repository_identity()
        session = chat_storage.rename_chat_session(key, session_id, title)
        if session is None:
            raise HTTPException(status_code=404, detail="Chat session was not found.")
        return session

    def ensure_session(self, session_id=None):
        if session_id:
            return self.get_session(session_id)
        sessions = self.list_sessions()
        return self.get_session(sessions[0]["session_id"]) if sessions else self.create_session()

    def answer(self, question, session_id=None):
        session = self.ensure_session(session_id)
        key = session["repository_key"]
        manager = self.state.repository_manager
        user_message = {"role": "user", "content": question}
        chat_storage.append_chat_messages(key, session["session_id"], [user_message])

        try:
            result = manager.get_rag_pipeline().answer(question)
        except Exception:
            logger.exception("Chat request failed")
            raise

        assistant_message = {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        }
        updated = chat_storage.append_chat_messages(
            key,
            session["session_id"],
            [assistant_message],
        )
        return {
            "session_id": session["session_id"],
            "repository": manager.get_repository(),
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
            "messages": updated.get("messages", []) if updated else [
                user_message,
                assistant_message,
            ],
        }
