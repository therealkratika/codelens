import os


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


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    "coverage"
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

            extension = os.path.splitext(file)[1]

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

                relative_path = os.path.relpath(
                    file_path,
                    repo_path
                )

                documents.append({
                    "file": relative_path,
                    "content": content
                })

            except Exception as e:
                print(f"Could not read {file_path}: {e}")

    return documents