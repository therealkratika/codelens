import hashlib
import re
import shutil
from pathlib import Path
from urllib.parse import urlsplit

from git import Repo


def validate_repository_url(repo_url: str) -> str:
    """Validate and normalize the public GitHub URL accepted by the API."""
    normalized_url = repo_url.strip()
    parsed = urlsplit(normalized_url)
    hostname = parsed.hostname

    if (
        parsed.scheme.lower() != "https"
        or hostname is None
        or hostname.lower() != "github.com"
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "Only public HTTPS GitHub repository URLs are supported."
        )

    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError(
            "Only public HTTPS GitHub repository URLs are supported."
        ) from error

    if port is not None:
        raise ValueError(
            "Only public HTTPS GitHub repository URLs are supported."
        )

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2 or parts[0] in {".", ".."} or parts[1] in {".", ".."}:
        raise ValueError(
            "Repository URL must have the form "
            "https://github.com/owner/repository."
        )

    return normalized_url


def clone_repository(repo_url: str, repo_name: str):
    repo_url = validate_repository_url(repo_url)
    backend_root = Path(__file__).resolve().parents[2]
    base_path = backend_root / "repositories"
    url_hash = hashlib.sha1(repo_url.encode("utf-8")).hexdigest()[:10]
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", repo_name)
    repo_path = base_path / f"{safe_name}_{url_hash}"

    base_path.mkdir(parents=True, exist_ok=True)
    if repo_path.exists():
        shutil.rmtree(repo_path)

    print(f"Cloning repository: {repo_url}")

    Repo.clone_from(
        repo_url,
        str(repo_path),
        multi_options=["--depth=1"],
    )

    print(f"Repository cloned to: {repo_path}")

    return str(repo_path)