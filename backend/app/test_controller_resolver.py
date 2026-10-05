from app.rag.route_analyzer import RouteAnalyzer
from app.rag.controller_resolver import ControllerResolver


REPOSITORY_ROOT = "./repositories/Nextja_coding_battle"

analyzer = RouteAnalyzer()

resolver = ControllerResolver(
    REPOSITORY_ROOT
)


# ---------------------------------------------------------
# Read server.js
# ---------------------------------------------------------

server_path = (
    f"{REPOSITORY_ROOT}/backend/server.js"
)

with open(
    server_path,
    "r",
    encoding="utf-8"
) as file:

    server_code = file.read()


# ---------------------------------------------------------
# Read battleRoutes.js
# ---------------------------------------------------------

route_path = (
    f"{REPOSITORY_ROOT}"
    "/backend/src/routes/battleRoutes.js"
)

with open(
    route_path,
    "r",
    encoding="utf-8"
) as file:

    route_code = file.read()


# ---------------------------------------------------------
# Analyze
# ---------------------------------------------------------

mounts = analyzer.analyze_mounts(
    "backend/server.js",
    server_code
)

routes = analyzer.analyze_route_file(
    "backend/src/routes/battleRoutes.js",
    route_code
)

full_routes = analyzer.build_full_routes(
    mounts,
    routes
)


# ---------------------------------------------------------
# Resolve controllers
# ---------------------------------------------------------

print("=" * 70)
print("ROUTE → CONTROLLER")
print("=" * 70)

for route in full_routes:

    controller = resolver.resolve(
        route["route_file"],
        route["handler"]
    )

    print()

    print(
        f"{route['method']} "
        f"{route['path']}"
    )

    print(
        f"  Handler: {route['handler']}"
    )

    print(
        f"  Controller: {controller}"
    )