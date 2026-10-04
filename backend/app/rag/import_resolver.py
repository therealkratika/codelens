import os


class ImportResolver:

    EXTENSIONS = [
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".py",
    ]

    def __init__(self, repository_root):
        self.repository_root = repository_root

    def resolve(self, current_file, import_source):

        # Ignore external packages
        if not import_source.startswith("."):
            return None

        current_path = os.path.join(
            self.repository_root,
            current_file
        )

        current_dir = os.path.dirname(current_path)

        target = os.path.normpath(
            os.path.join(
                current_dir,
                import_source
            )
        )

        # Exact file
        if os.path.isfile(target):
            return self.relative_path(target)

        # Try extensions
        for extension in self.EXTENSIONS:

            candidate = target + extension

            if os.path.isfile(candidate):
                return self.relative_path(candidate)

        # Try index files
        for extension in self.EXTENSIONS:

            candidate = os.path.join(
                target,
                "index" + extension
            )

            if os.path.isfile(candidate):
                return self.relative_path(candidate)

        return None

    def relative_path(self, absolute_path):

        return os.path.relpath(
            absolute_path,
            self.repository_root
        ).replace("\\", "/")