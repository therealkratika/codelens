from app.rag.feature_flow import FeatureFlowAnalyzer


REPOSITORY_ROOT = "repositories/Nextja_coding_battle"

analyzer = FeatureFlowAnalyzer(REPOSITORY_ROOT)

API_FILE = "frontend/lib/api.ts"
SERVER_FILE = "backend/server.js"
ROUTE_FILE = "backend/src/routes/battleRoutes.js"


print("=" * 70)
print("FULL FEATURE FLOW TEST")
print("=" * 70)

# 1. Analyze frontend APIs

api_results = analyzer.trace_frontend_api(API_FILE)

print("\nFRONTEND APIs")
print("-" * 70)

for api in api_results:
    print(
        f"{api['function']} "
        f"→ {api['method']} "
        f"{api['resolved_endpoint']}"
    )

# 2. Select joinBattle API

join_api = None

for api in api_results:

    if api["function"] == "joinBattle":

        join_api = api
        break


if join_api is None:

    print("\n❌ joinBattle API not found")
    raise SystemExit(1)


print("\nSELECTED FRONTEND API")
print("-" * 70)

print(
    f"{join_api['function']} "
    f"→ {join_api['method']} "
    f"{join_api['resolved_endpoint']}"
)

# 3. Trace backend route


backend_flow = analyzer.trace_route(
    route_file=ROUTE_FILE,
    server_file=SERVER_FILE,
    handler="joinBattle"
)


if backend_flow is None:

    print("\n❌ Backend route not found")
    raise SystemExit(1)

# 4. Match frontend API with backend route

matched = analyzer.match_api_to_route(
    join_api,
    backend_flow
)


print("\nAPI → ROUTE MATCH")
print("-" * 70)

if matched:

    print("✅ MATCH FOUND")

else:

    print("MATCH NOT FOUND")

# 5. Display complete flow

print("\n" + "=" * 70)
print("COMPLETE FEATURE FLOW")
print("=" * 70)

print(
    f"\nFrontend API\n"
    f"  {join_api['file']}:{join_api['line']}\n"
    f"  {join_api['function']}()"
)

print(
    f"\nHTTP Request\n"
    f"  {join_api['method']} "
    f"{join_api['resolved_endpoint']}"
)

route = backend_flow["route"]

print(
    f"\nBackend Route\n"
    f"  {route['route_file']}:{route['route_line']}\n"
    f"  {route['method']} {route['path']}"
)

controller = backend_flow["controller"]

print(
    f"\nController\n"
    f"  {controller['controller_file']}\n"
    f"  {controller['controller_function']}\n"
    f"  Lines: "
    f"{controller['controller_start_line']}-"
    f"{controller['controller_end_line']}"
)

print("\nDependencies")

for dependency in backend_flow["dependencies"]:

    print(
        f"  {dependency['symbol']} "
        f"→ {dependency['target_file']}"
    )


print("\n" + "=" * 70)

if matched:
    print("FULL FEATURE FLOW SUCCESS")
else:
    print("FEATURE FLOW MATCH FAILED")

print("=" * 70)