import hashlib
import re
import shutil
from pathlib import Path
from git import Repo


def clone_repository(repo_url: str, repo_name: str):
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