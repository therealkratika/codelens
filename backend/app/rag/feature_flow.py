from app.rag.route_analyzer import RouteAnalyzer
from app.rag.controller_resolver import ControllerResolver
from app.rag.dependency_resolver import DependencyResolver


class FeatureFlowAnalyzer:

    def __init__(self, repository_root):
        self.repository_root = repository_root

        self.route_analyzer = RouteAnalyzer()

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
        # Find mounts
        mounts = self.route_analyzer.analyze_mounts(
            server_file,
            server_code
        )
        # Find routes

        routes = self.route_analyzer.analyze_route_file(
            route_file,
            route_code
        )

        full_routes = self.route_analyzer.build_full_routes(
            mounts,
            routes
        )
        # Find requested route

        selected_route = None

        for route in full_routes:

            if route["handler"] == handler:

                selected_route = route

                break

        if selected_route is None:
            return None

        # Resolve controller
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
        # Read controller
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

        # Find function dependencies
        dependencies = (
            self.dependency_resolver
            .trace_function_dependencies(
                controller_file,
                controller_code,
                handler
            )
        )
        # Final flow

        return {
            "route": selected_route,
            "controller": controller,
            "dependencies": dependencies
        }