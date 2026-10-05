from app.rag.feature_flow import FeatureFlowAnalyzer


REPOSITORY_ROOT = "repositories/Nextja_coding_battle"

API_FILE = "frontend/lib/api.ts"
SERVER_FILE = "backend/server.js"
ROUTE_FILE = "backend/src/routes/battleRoutes.js"


analyzer = FeatureFlowAnalyzer(REPOSITORY_ROOT)

print("=" * 70)
print("API → BACKEND FEATURE FLOW TEST")
print("=" * 70)


# --------------------------------------------------
# 1. Analyze frontend API
# --------------------------------------------------

api_results = analyzer.trace_frontend_api(API_FILE)

print("\nFRONTEND APIs")
print("-" * 70)

for api in api_results:
    print(
        f"{api['function']} "
        f"→ {api['method']} "
        f"{api['resolved_endpoint']}"
    )

print("\nDIRECT API FEATURE FLOW")
print("-" * 70)
flow = analyzer.trace_api_feature_flow(
    api_file=API_FILE,
    api_function="joinBattle"
)
print(flow)


# --------------------------------------------------
# 2. Test each API against backend routes
# --------------------------------------------------

print("\nMATCHED FEATURE FLOWS")
print("-" * 70)

matches = 0

for api in api_results:

    backend_flow = analyzer.trace_route(
        route_file=ROUTE_FILE,
        server_file=SERVER_FILE,
        handler=api["function"]
    )

    if backend_flow is None:
        continue

    matched = analyzer.match_api_to_route(
        api,
        backend_flow
    )

    if not matched:
        continue

    matches += 1

    route = backend_flow["route"]
    controller = backend_flow["controller"]

    print("\n" + "-" * 70)

    print(
        f"Frontend API:\n"
        f"  {api['function']}()\n"
        f"  {api['file']}:{api['line']}"
    )

    print(
        f"\nHTTP:\n"
        f"  {api['method']} "
        f"{api['resolved_endpoint']}"
    )

    print(
        f"\nBackend Route:\n"
        f"  {route['route_file']}:{route['route_line']}\n"
        f"  {route['method']} {route['path']}"
    )

    if controller:

        print(
            f"\nController:\n"
            f"  {controller['controller_file']}\n"
            f"  {controller['controller_function']}\n"
            f"  Lines: "
            f"{controller['controller_start_line']}-"
            f"{controller['controller_end_line']}"
        )

    print("\nDependencies:")

    for dependency in backend_flow["dependencies"]:

        print(
            f"  {dependency['symbol']} "
            f"→ {dependency['target_file']}"
        )


print("\n" + "=" * 70)
print(f"TOTAL MATCHES: {matches}")
print("=" * 70)