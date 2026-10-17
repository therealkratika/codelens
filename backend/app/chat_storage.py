from datetime import datetime, timezone
from uuid import uuid4

from pymongo import ReturnDocument

from app.config import database


chat_sessions_collection = database["chat_sessions"]


def _now():
    return datetime.now(timezone.utc)


def create_chat_session(repository_key, repository, repository_path, title=None):
    now = _now()
    session = {
        "session_id": str(uuid4()),
        "repository_key": repository_key,
        "repository": repository,
        "repository_path": repository_path,
        "title": (title or "New chat").strip()[:120] or "New chat",
        "messages": [],
        "created_at": now,
        "updated_at": now,
    }
    chat_sessions_collection.insert_one(session)
    return _without_id(session)


def list_chat_sessions(repository_key):
    return [
        _without_id(session)
        for session in chat_sessions_collection.find(
            {"repository_key": repository_key},
            {
                "_id": 0,
                "session_id": 1,
                "repository": 1,
                "repository_path": 1,
                "title": 1,
                "created_at": 1,
                "updated_at": 1,
            },
        ).sort("updated_at", -1)
    ]


def get_chat_session(repository_key, session_id):
    session = chat_sessions_collection.find_one(
        {"repository_key": repository_key, "session_id": session_id},
        {"_id": 0},
    )
    return session


def append_chat_messages(repository_key, session_id, messages):
    result = chat_sessions_collection.find_one_and_update(
        {"repository_key": repository_key, "session_id": session_id},
        {
            "$push": {"messages": {"$each": messages}},
            "$set": {"updated_at": _now()},
        },
        projection={"_id": 0},
        return_document=ReturnDocument.AFTER,
    )
    return result


def delete_chat_session(repository_key, session_id):
    result = chat_sessions_collection.delete_one(
        {"repository_key": repository_key, "session_id": session_id}
    )
    return result.deleted_count > 0


def rename_chat_session(repository_key, session_id, title):
    return chat_sessions_collection.find_one_and_update(
        {"repository_key": repository_key, "session_id": session_id},
        {"$set": {"title": title[:120], "updated_at": _now()}},
        projection={"_id": 0},
        return_document=ReturnDocument.AFTER,
    )


def _without_id(document):
    if document is None:
        return None
    document.pop("_id", None)
    return document
