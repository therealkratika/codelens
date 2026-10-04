import os


# File types that CodeLens should index
SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".md"
}


# Directories that should NOT be indexed
IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    "coverage",
    ".cache",
    "out",
    "target"
}


# Individual files that should NOT be indexed
IGNORED_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    ".DS_Store"
}


def load_files(repo_path: str):

    documents = []

    for root, dirs, files in os.walk(repo_path):

        # Remove ignored directories
        dirs[:] = [
            directory
            for directory in dirs
            if directory not in IGNORED_DIRECTORIES
        ]

        for file in files:

            # Ignore unnecessary files
            if file in IGNORED_FILES:
                continue

            # Get file extension
            extension = os.path.splitext(file)[1].lower()

            # Only process supported file types
            if extension not in SUPPORTED_EXTENSIONS:
                continue

            file_path = os.path.join(root, file)

            try:

                with open(
                    file_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as f:

                    content = f.read()

                # Skip completely empty files
                if not content.strip():
                    continue

                # Path relative to repository root
                relative_path = os.path.relpath(
                    file_path,
                    repo_path
                )

                documents.append({
                    "file": relative_path,
                    "content": content
                })

            except Exception as e:

                print(
                    f"Could not read {file_path}: {e}"
                )

    return documents