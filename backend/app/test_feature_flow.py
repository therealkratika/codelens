from app.rag.feature_flow import FeatureFlowAnalyzer


REPOSITORY_ROOT = "./repositories/Nextja_coding_battle"

analyzer = FeatureFlowAnalyzer(
    REPOSITORY_ROOT
)


SERVER_FILE = "backend/server.js"

ROUTE_FILE = (
    "backend/src/routes/battleRoutes.js"
)


functions_to_test = [
    "createBattle",
    "joinBattle",
    "getBattleQuestions",
]


for function_name in functions_to_test:

    result = analyzer.trace_route(
        route_file=ROUTE_FILE,
        server_file=SERVER_FILE,
        handler=function_name
    )

    print()
    print("=" * 70)
    print(function_name)
    print("=" * 70)

    if result is None:

        print("No route found.")

        continue

    route = result["route"]
    controller = result["controller"]
    dependencies = result["dependencies"]

    print()
    print("ROUTE")
    print(
        f"{route['method']} "
        f"{route['path']}"
    )

    print()
    print("CONTROLLER")

    if controller:

        print(
            f"{controller['controller_file']}"
        )

        print(
            f"Function: "
            f"{controller['controller_function']}"
        )

        print(
            f"Lines: "
            f"{controller['controller_start_line']}-"
            f"{controller['controller_end_line']}"
        )

    else:

        print("Not resolved.")

    print()
    print("DEPENDENCIES")

    for dependency in dependencies:

        print(
            f"{dependency['symbol']}"
            f" → "
            f"{dependency['target_file']}"
        )