import re


class RouteAnalyzer:

    ROUTE_METHODS = {
        "get": "GET",
        "post": "POST",
        "put": "PUT",
        "patch": "PATCH",
        "delete": "DELETE",
    }

    def analyze_route_file(self, file_path, code):
        """
        Analyze an Express route file.

        Example:

        router.post("/create", createBattle)

        becomes:

        {
            "method": "POST",
            "path": "/create",
            "handler": "createBattle",
            "file": "backend/src/routes/battleRoutes.js"
        }
        """

        results = []

        pattern = re.compile(
            r"router\."
            r"(get|post|put|patch|delete)"
            r"\s*\("
            r"\s*[\"'`]([^\"'`]+)[\"'`]"
            r"\s*,\s*"
            r"(?:require\([^)]*\)\.)?"
            r"([A-Za-z_$][\w$]*)",
            re.IGNORECASE,
        )

        for match in pattern.finditer(code):

            method = self.ROUTE_METHODS[match.group(1).lower()]
            path = match.group(2)
            handler = match.group(3)

            line = code[:match.start()].count("\n") + 1

            results.append({
                "method": method,
                "path": path,
                "handler": handler,
                "file": file_path,
                "line": line,
            })

        return results


    def analyze_mounts(self, file_path, code):
        """
        Analyze Express route mounting.

        Example:

        app.use("/api/battle", battleRoutes)

        becomes:

        {
            "prefix": "/api/battle",
            "router": "battleRoutes"
        }
        """

        results = []

        pattern = re.compile(
            r"app\.use"
            r"\s*\("
            r"\s*[\"'`]([^\"'`]+)[\"'`]"
            r"\s*,\s*"
            r"([A-Za-z_$][\w$]*)",
            re.MULTILINE,
        )

        for match in pattern.finditer(code):

            prefix = match.group(1)
            router = match.group(2)

            line = code[:match.start()].count("\n") + 1

            results.append({
                "prefix": prefix,
                "router": router,
                "file": file_path,
                "line": line,
            })

        return results


    def build_full_routes(self, mounts, routes):
        """
        Combine:

        app.use("/api/battle", battleRoutes)

        with:

        router.post("/create", createBattle)

        into:

        POST /api/battle/create
        """

        results = []

        for route in routes:

            for mount in mounts:

                route_file_name = route["file"].split("/")[-1]

                expected_router_file = (
                    mount["router"].replace("Routes", "Routes") + ".js"
                )

                if route_file_name != expected_router_file:
                    continue

                full_path = (
                    mount["prefix"].rstrip("/")
                    + "/"
                    + route["path"].lstrip("/")
                )

                results.append({
                    "method": route["method"],
                    "path": full_path,
                    "handler": route["handler"],
                    "route_file": route["file"],
                    "route_line": route["line"],
                    "mount_file": mount["file"],
                    "mount_line": mount["line"],
                })

        return results