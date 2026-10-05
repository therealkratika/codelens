import os
import re


class DependencyResolver:

    EXTENSIONS = [".js", ".jsx", ".ts", ".tsx"]

    def __init__(self, repository_root):
        self.repository_root = repository_root

    def analyze_file(self, file_path, code):
        """
        Analyze dependencies imported by a JavaScript/TypeScript file.

        Supports:

        const Battle = require("../model/battle.js");

        const {
            sanitizeQuestion
        } = require("../services/questionService.js");

        const leaderboardService =
            require("../services/leaderboardService");

        Returns structured dependency information.
        """

        dependencies = []

        # ---------------------------------------------------------
        # Pattern 1:
        #
        # const Battle = require("../model/battle.js");
        # ---------------------------------------------------------

        default_pattern = re.compile(
            r"const\s+"
            r"([A-Za-z_$][\w$]*)"
            r"\s*=\s*require"
            r"\s*\(\s*[\"']([^\"']+)[\"']\s*\)",
            re.MULTILINE,
        )

        for match in default_pattern.finditer(code):

            symbol = match.group(1)
            import_source = match.group(2)

            target_file = self._resolve_import(
                file_path,
                import_source
            )

            dependencies.append({
                "symbol": symbol,
                "import_source": import_source,
                "target_file": target_file,
                "type": "default"
            })

        # ---------------------------------------------------------
        # Pattern 2:
        #
        # const {
        #     sanitizeQuestion
        # } = require("../services/questionService.js");
        # ---------------------------------------------------------

        destructured_pattern = re.compile(
            r"const\s*\{([\s\S]*?)\}"
            r"\s*=\s*require"
            r"\s*\(\s*[\"']([^\"']+)[\"']\s*\)",
            re.MULTILINE,
        )

        for match in destructured_pattern.finditer(code):

            imported_names = match.group(1)
            import_source = match.group(2)

            names = self._parse_destructured_names(
                imported_names
            )

            target_file = self._resolve_import(
                file_path,
                import_source
            )

            for symbol in names:

                dependencies.append({
                    "symbol": symbol,
                    "import_source": import_source,
                    "target_file": target_file,
                    "type": "destructured"
                })

        return dependencies

    def trace_function_dependencies(
        self,
        file_path,
        code,
        function_name
    ):
        """
        Find which imported dependencies are actually used
        inside a specific function.
        """

        dependencies = self.analyze_file(
            file_path,
            code
        )

        function_code = self._extract_function_code(
            code,
            function_name
        )

        if function_code is None:
            return []

        results = []

        for dependency in dependencies:
            symbol = dependency["symbol"]

            pattern = re.compile(
                rf"\b{re.escape(symbol)}\b"
            )

            if pattern.search(function_code):
                results.append(dependency)

        return results

    def _extract_function_code(self, code, function_name):

        escaped_name = re.escape(function_name)

        declaration_pattern = re.compile(
            rf"(?:async\s+)?function\s+{escaped_name}\s*"
            rf"\([^)]*\)\s*\{{"
        )

        arrow_pattern = re.compile(
            rf"(?:const|let|var)\s+{escaped_name}\s*=\s*"
            rf"(?:async\s*)?"
            rf"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>\s*\{{"
        )

        match = declaration_pattern.search(code)

        if match is None:
            match = arrow_pattern.search(code)

        if match is None:
            return None

        body_start = match.end() - 1
        brace_depth = 0
        quote = None
        escaped = False
        line_comment = False
        block_comment = False
        index = body_start

        while index < len(code):
            character = code[index]
            next_character = (
                code[index + 1]
                if index + 1 < len(code)
                else ""
            )

            if line_comment:
                if character == "\n":
                    line_comment = False
            elif block_comment:
                if character == "*" and next_character == "/":
                    block_comment = False
                    index += 1
            elif quote is not None:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == quote:
                    quote = None
            elif character == "/" and next_character == "/":
                line_comment = True
                index += 1
            elif character == "/" and next_character == "*":
                block_comment = True
                index += 1
            elif character in {"'", '"', "`"}:
                quote = character
            elif character == "{":
                brace_depth += 1
            elif character == "}":
                brace_depth -= 1

                if brace_depth == 0:
                    return code[match.start():index + 1]

            index += 1

        return code[match.start():]

    def _parse_destructured_names(self, text):
        names = []

        for item in text.split(","):

            item = item.strip()

            if not item:
                continue

            # Handles:
            #
            # sanitizeQuestion
            #
            # sanitizeQuestion: sanitize

            if ":" in item:

                imported, alias = item.split(
                    ":",
                    1
                )

                names.append(
                    alias.strip()
                )

            else:

                names.append(item)

        return names

    def _resolve_import(
        self,
        current_file,
        import_source
    ):
        """
        Resolve a relative CommonJS import.
        """

        if not import_source.startswith("."):
            return None

        current_absolute = os.path.join(
            self.repository_root,
            current_file
        )

        current_directory = os.path.dirname(
            current_absolute
        )

        target = os.path.normpath(
            os.path.join(
                current_directory,
                import_source
            )
        )

        # Exact path
        if os.path.isfile(target):
            return self._relative_path(target)

        # Add extensions
        for extension in self.EXTENSIONS:

            candidate = target + extension

            if os.path.isfile(candidate):

                return self._relative_path(
                    candidate
                )

        # index files
        for extension in self.EXTENSIONS:

            candidate = os.path.join(
                target,
                "index" + extension
            )

            if os.path.isfile(candidate):

                return self._relative_path(
                    candidate
                )

        return None

    def _relative_path(self, absolute_path):

        return os.path.relpath(
            absolute_path,
            self.repository_root
        ).replace("\\", "/")