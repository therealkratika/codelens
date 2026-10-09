
from datetime import datetime, timezone

from app.config import database


repositories_collection = database["repositories"]
settings_collection = database["settings"]


def normalize_repo_url(repo_url: str) -> str:
    return (
        repo_url.strip()
        .rstrip("/")
        .removesuffix(".git")
        .lower()
    )


def save_repository(repository: dict) -> dict:
    repo_url = repository.get("repo_url")

    if not repo_url:
        raise ValueError("Repository URL is required.")

    normalized_url = normalize_repo_url(repo_url)
    now = datetime.now(timezone.utc)

    document = {
        "normalized_url": normalized_url,
        "repo_url": repo_url,
        "repository": repository["repository"],
        "repository_path": repository["repository_path"],
        "files": repository.get("files", 0),
        "chunks": repository.get("chunks", 0),
        "status": repository.get("status", "indexed"),
        "updated_at": now,
    }

    repositories_collection.update_one(
        {"normalized_url": normalized_url},
        {
            "$set": document,
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )

    return repositories_collection.find_one(
        {"normalized_url": normalized_url},
        {"_id": 0},
    )


def get_saved_repositories() -> list:
    return list(
        repositories_collection.find(
            {},
            {"_id": 0},
        ).sort("updated_at", -1)
    )


def get_repository_by_url(repo_url: str):
    return repositories_collection.find_one(
        {
            "normalized_url": normalize_repo_url(repo_url)
        },
        {"_id": 0},
    )


def delete_repository(repo_url: str) -> bool:
    result = repositories_collection.delete_one(
        {
            "normalized_url": normalize_repo_url(repo_url)
        }
    )
    return result.deleted_count > 0


def set_active_repository(repository_path):
    settings_collection.update_one(
        {"_id": "repository_state"},
        {
            "$set": {
                "active_repository_path": repository_path,
                "updated_at": datetime.now(timezone.utc),
            }
        },
        upsert=True,
    )


def get_active_repository_path():
    state = settings_collection.find_one(
        {"_id": "repository_state"}
    )

    if state is None:
        return None

    return state.get("active_repository_path")
