import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    backend_root = Path(__file__).resolve().parent.parent
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

from app.rag.route_analyzer import RouteAnalyzer


analyzer = RouteAnalyzer()

repository_root = "./repositories/Nextja_coding_battle"


# ---------------------------------------------------------
# Read server.js
# ---------------------------------------------------------

server_path = (
    f"{repository_root}/backend/server.js"
)

with open(server_path, "r", encoding="utf-8") as file:
    server_code = file.read()


# ---------------------------------------------------------
# Read battleRoutes.js
# ---------------------------------------------------------

route_path = (
    f"{repository_root}/backend/src/routes/battleRoutes.js"
)

with open(route_path, "r", encoding="utf-8") as file:
    route_code = file.read()


# ---------------------------------------------------------
# Analyze mounts
# ---------------------------------------------------------

mounts = analyzer.analyze_mounts(
    "backend/server.js",
    server_code
)


print("=" * 70)
print("MOUNTS")
print("=" * 70)

for mount in mounts:
    print(mount)


# ---------------------------------------------------------
# Analyze routes
# ---------------------------------------------------------

routes = analyzer.analyze_route_file(
    "backend/src/routes/battleRoutes.js",
    route_code
)


print()
print("=" * 70)
print("ROUTES")
print("=" * 70)

for route in routes:
    print(route)


# ---------------------------------------------------------
# Build complete routes
# ---------------------------------------------------------

full_routes = analyzer.build_full_routes(
    mounts,
    routes
)


print()
print("=" * 70)
print("FULL ROUTES")
print("=" * 70)

for route in full_routes:
    print(route)