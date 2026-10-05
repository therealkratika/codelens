import os
from urllib.parse import urlsplit

from app.rag.route_analyzer import RouteAnalyzer
from app.rag.controller_resolver import ControllerResolver
from app.rag.dependency_resolver import DependencyResolver
from app.rag.api_flow_analyzer import APIFlowAnalyzer


class FeatureFlowAnalyzer:

    def __init__(self, repository_root):
        self.repository_root = repository_root

        self.route_analyzer = RouteAnalyzer()

        self.api_flow_analyzer = APIFlowAnalyzer()

        self.controller_resolver = ControllerResolver(
            repository_root
        )

        self.dependency_resolver = DependencyResolver(
            repository_root
        )

    def trace_route(
        self,
        route_file,
        server_file,
        handler
    ):
        """
        Trace a backend route from:

        route
          ↓
        controller
          ↓
        function dependencies
        """

        server_path = (
            f"{self.repository_root}/{server_file}"
        )

        route_path = (
            f"{self.repository_root}/{route_file}"
        )

        with open(
            server_path,
            "r",
            encoding="utf-8"
        ) as file:

            server_code = file.read()

        with open(
            route_path,
            "r",
            encoding="utf-8"
        ) as file:

            route_code = file.read()

        # -----------------------------------
        # Find API mounts
        # -----------------------------------

        mounts = self.route_analyzer.analyze_mounts(
            server_file,
            server_code
        )

        # -----------------------------------
        # Find routes
        # -----------------------------------

        routes = self.route_analyzer.analyze_route_file(
            route_file,
            route_code
        )

        # -----------------------------------
        # Build complete routes
        # -----------------------------------

        full_routes = self.route_analyzer.build_full_routes(
            mounts,
            routes
        )

        # -----------------------------------
        # Find requested route
        # -----------------------------------

        selected_route = None

        for route in full_routes:

            if route["handler"] == handler:

                selected_route = route

                break

        if selected_route is None:
            return None

        # -----------------------------------
        # Resolve controller
        # -----------------------------------

        controller = (
            self.controller_resolver.resolve(
                route_file,
                handler
            )
        )

        if controller is None:

            return {
                "route": selected_route,
                "controller": None,
                "dependencies": []
            }

        # -----------------------------------
        # Read controller
        # -----------------------------------

        controller_file = controller[
            "controller_file"
        ]

        controller_path = (
            f"{self.repository_root}/"
            f"{controller_file}"
        )

        with open(
            controller_path,
            "r",
            encoding="utf-8"
        ) as file:

            controller_code = file.read()

        # -----------------------------------
        # Find function dependencies
        # -----------------------------------

        dependencies = (
            self.dependency_resolver
            .trace_function_dependencies(
                controller_file,
                controller_code,
                handler
            )
        )

        # -----------------------------------
        # Final backend flow
        # -----------------------------------

        return {
            "route": selected_route,
            "controller": controller,
            "dependencies": dependencies
        }

    def trace_frontend_api(self, api_file):
        """
        Analyze a frontend API file.

        Flow:

        Frontend API function
              ↓
        HTTP method
              ↓
        Endpoint
              ↓
        Resolved backend endpoint
        """

        api_path = (
            f"{self.repository_root}/{api_file}"
        )

        with open(
            api_path,
            "r",
            encoding="utf-8"
        ) as file:

            api_code = file.read()

        return self.api_flow_analyzer.analyze(
            api_file,
            api_code
        )

    def match_api_to_route(self, api, backend_flow):
        """Return whether a frontend API matches a backend route."""

        route = backend_flow.get("route")

        if not route:
            return False

        api_method = api.get("method", "").upper()
        route_method = route.get("method", "").upper()

        if not api_method or api_method != route_method:
            return False

        endpoint = api.get("resolved_endpoint", "")

        if not endpoint:
            return False

        endpoint_path = urlsplit(endpoint).path
        route_path = route.get("path", "")

        if not route_path:
            return False

        endpoint_path = endpoint_path.rstrip("/") or "/"
        route_path = route_path.rstrip("/") or "/"
        endpoint_segments = endpoint_path.strip("/").split("/")
        route_segments = route_path.strip("/").split("/")

        if len(endpoint_segments) != len(route_segments):
            return False

        for endpoint_segment, route_segment in zip(
            endpoint_segments,
            route_segments
        ):
            is_route_parameter = route_segment.startswith(":")
            is_frontend_parameter = (
                endpoint_segment.startswith("${")
                and endpoint_segment.endswith("}")
            )

            if is_route_parameter:
                if not endpoint_segment:
                    return False
                continue

            if is_frontend_parameter:
                continue

            if endpoint_segment != route_segment:
                return False

        return True

    def trace_api_feature_flow(
        self,
        api_file,
        api_function
    ):
        """Trace a frontend API function to its backend route and dependencies."""

        api_results = self.trace_frontend_api(api_file)
        selected_api = next(
            (
                api
                for api in api_results
                if api.get("function") == api_function
            ),
            None
        )

        if selected_api is None:
            return None

        ignored_directories = {
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            "dist",
            "build",
            ".next"
        }
        source_extensions = {
            ".js",
            ".jsx",
            ".ts",
            ".tsx"
        }

        for root, directories, filenames in os.walk(
            self.repository_root
        ):
            directories[:] = sorted(
                directory
                for directory in directories
                if directory not in ignored_directories
            )

            for filename in sorted(filenames):
                if os.path.splitext(filename)[1].lower() not in source_extensions:
                    continue

                absolute_path = os.path.join(root, filename)
                route_file = os.path.relpath(
                    absolute_path,
                    self.repository_root
                ).replace("\\", "/")

                try:
                    with open(
                        absolute_path,
                        "r",
                        encoding="utf-8"
                    ) as file:
                        route_code = file.read()

                except (OSError, UnicodeDecodeError):
                    continue

                routes = self.route_analyzer.analyze_route_file(
                    route_file,
                    route_code
                )

                if not routes:
                    continue

                server_file = self._find_server_file(
                    route_file
                )

                if server_file is None:
                    continue

                for route in routes:
                    handler = route.get("handler")

                    if not handler:
                        continue

                    flow = self.trace_route(
                        route_file=route_file,
                        server_file=server_file,
                        handler=handler
                    )

                    if (
                        flow is not None
                        and self.match_api_to_route(
                            selected_api,
                            flow
                        )
                    ):
                        flow["frontend_api"] = selected_api
                        return flow

        return None

    def _find_server_file(self, route_file):

        route_name = os.path.splitext(
            os.path.basename(route_file)
        )[0]

        ignored_directories = {
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            "dist",
            "build",
            ".next"
        }
        source_extensions = {
            ".js",
            ".jsx",
            ".ts",
            ".tsx"
        }
        preferred_names = {
            "server.js",
            "server.ts",
            "app.js",
            "app.ts",
            "index.js",
            "index.ts",
            "main.js",
            "main.ts"
        }
        candidates = []

        for root, directories, filenames in os.walk(
            self.repository_root
        ):
            directories[:] = sorted(
                directory
                for directory in directories
                if directory not in ignored_directories
            )

            for filename in sorted(filenames):
                if os.path.splitext(filename)[1].lower() not in source_extensions:
                    continue

                absolute_path = os.path.join(root, filename)

                try:
                    with open(
                        absolute_path,
                        "r",
                        encoding="utf-8"
                    ) as file:
                        code = file.read()

                except (OSError, UnicodeDecodeError):
                    continue

                mounts = self.route_analyzer.analyze_mounts(
                    os.path.relpath(
                        absolute_path,
                        self.repository_root
                    ).replace("\\", "/"),
                    code
                )

                if any(
                    mount.get("router") == route_name
                    for mount in mounts
                ):
                    candidates.append(
                        os.path.relpath(
                            absolute_path,
                            self.repository_root
                        ).replace("\\", "/")
                    )

        candidates.sort(
            key=lambda path: (
                path.rsplit("/", 1)[-1].lower()
                not in preferred_names,
                path
            )
        )

        return candidates[0] if candidates else None