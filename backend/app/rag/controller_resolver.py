import re
import os


class ControllerResolver:

    def __init__(self, repository_root):
        self.repository_root = repository_root

    def resolve(self, route_file, handler):
        """
        Find the controller function used by a route.

        Example:

        route:
            router.post("/create", createBattle)

        route file imports:
            const { createBattle } =
                require("../controller/battleController");

        Returns:
            {
                "handler": "createBattle",
                "controller_file":
                    "backend/src/controller/battleController.js",
                "controller_function": "createBattle"
            }
        """

        route_absolute = os.path.join(
            self.repository_root,
            route_file
        )

        if not os.path.isfile(route_absolute):
            return None

        with open(route_absolute, "r", encoding="utf-8") as file:
            route_code = file.read()

        controller_file = self._find_controller_import(
            route_absolute,
            route_code,
            handler
        )

        if controller_file is None:
            return None

        controller_code = self._read_file(controller_file)

        if controller_code is None:
            return None

        function_info = self._find_function(
            controller_code,
            handler
        )

        if function_info is None:
            return None

        return {
            "handler": handler,
            "controller_file": self._relative_path(
                controller_file
            ),
            "controller_function": handler,
            "controller_start_line": function_info["start_line"],
            "controller_end_line": function_info["end_line"],
        }

    def _find_controller_import(
        self,
        route_absolute,
        route_code,
        handler
    ):
        """
        Find the controller file imported by the route file.
        """

        # Handles:

        # const {
        #   createBattle,
        #   joinBattle
        # } = require("../controller/battleController");

        pattern = re.compile(
            r"const\s*\{([\s\S]*?)\}"
            r"\s*=\s*require"
            r"\s*\(\s*[\"']([^\"']+)[\"']\s*\)",
            re.MULTILINE
        )

        for match in pattern.finditer(route_code):

            imported_names = match.group(1)
            import_path = match.group(2)

            names = [
                name.strip()
                for name in imported_names.split(",")
            ]

            names = [
                name.split(" as ")[0].strip()
                for name in names
            ]

            if handler not in names:
                continue

            return self._resolve_import_path(
                route_absolute,
                import_path
            )

        return None

    def _resolve_import_path(
        self,
        current_file,
        import_path
    ):
        """
        Resolve relative JS import to an actual file.
        """

        if not import_path.startswith("."):
            return None

        current_dir = os.path.dirname(current_file)

        target = os.path.normpath(
            os.path.join(
                current_dir,
                import_path
            )
        )

        extensions = [
            ".js",
            ".jsx",
            ".ts",
            ".tsx"
        ]

        # Exact file
        if os.path.isfile(target):
            return target

        # Add extension
        for extension in extensions:

            candidate = target + extension

            if os.path.isfile(candidate):
                return candidate

        # index.js
        for extension in extensions:

            candidate = os.path.join(
                target,
                "index" + extension
            )

            if os.path.isfile(candidate):
                return candidate

        return None

    def _read_file(self, file_path):

        if not os.path.isfile(file_path):
            return None

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    def _find_function(
        self,
        code,
        function_name
    ):
        """
        Find a function declaration such as:

        const createBattle = async (req, res) => {

        or:

        function createBattle(req, res) {
        """

        patterns = [

            re.compile(
                rf"const\s+{re.escape(function_name)}"
                r"\s*=\s*(?:async\s*)?"
                r"\([^)]*\)\s*=>",
                re.MULTILINE
            ),

            re.compile(
                rf"function\s+{re.escape(function_name)}"
                r"\s*\(",
                re.MULTILINE
            ),

            re.compile(
                rf"const\s+{re.escape(function_name)}"
                r"\s*=\s*(?:async\s*)?"
                r"[A-Za-z_$][\w$]*\s*=>",
                re.MULTILINE
            ),
        ]

        for pattern in patterns:

            match = pattern.search(code)

            if not match:
                continue

            start_line = (
                code[:match.start()]
                .count("\n") + 1
            )

            # Find approximate end of function.
            end_line = self._find_function_end(
                code,
                match.start()
            )

            return {
                "start_line": start_line,
                "end_line": end_line
            }

        return None

    def _find_function_end(
        self,
        code,
        start
    ):
        """
        Approximate function end using brace balancing.
        """

        opening_brace = code.find(
            "{",
            start
        )

        if opening_brace == -1:
            return code[start:].count("\n") + 1

        depth = 0

        for index in range(
            opening_brace,
            len(code)
        ):

            character = code[index]

            if character == "{":
                depth += 1

            elif character == "}":
                depth -= 1

                if depth == 0:

                    return (
                        code[:index]
                        .count("\n") + 1
                    )

        return code[start:].count("\n") + 1

    def _relative_path(
        self,
        absolute_path
    ):
        return os.path.relpath(
            absolute_path,
            self.repository_root
        ).replace("\\", "/")