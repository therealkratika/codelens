import os
import shutil
from git import Repo


def clone_repository(repo_url: str, repo_name: str):
    base_path = "repositories"
    repo_path = os.path.join(base_path, repo_name)
    # Remove existing repository if present
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)

    os.makedirs(base_path, exist_ok=True)

    print(f"Cloning repository: {repo_url}")

    Repo.clone_from(repo_url, repo_path)

    print(f"Repository cloned to: {repo_path}")

    return repo_path