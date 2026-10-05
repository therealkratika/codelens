from app.feature_flow_dataset import FEATURE_FLOW_DATASET
from app.rag.feature_flow import FeatureFlowAnalyzer


REPOSITORY_ROOT = "./repositories/Nextja_coding_battle"


def evaluate():
    analyzer = FeatureFlowAnalyzer(
        REPOSITORY_ROOT
    )

    total_checks = 0
    passed_checks = 0

    print("\n" + "=" * 70)
    print("CODELENS FEATURE-FLOW EVALUATION")
    print("=" * 70)

    for item in FEATURE_FLOW_DATASET:

        print("\n" + "-" * 70)
        print(item["name"])
        print("-" * 70)

        route_file = "backend/src/routes/battleRoutes.js"
        server_file = "backend/server.js"
        handler = item["controller_function"]

        try:
            result = analyzer.trace_route(
                route_file=route_file,
                server_file=server_file,
                handler=handler
            )
        except Exception as error:
            print(f"ERROR: {error}")
            continue

        if result is None:
            print("❌ Route could not be traced.")
            continue

        # ------------------------------------------------
        # Check route
        # ------------------------------------------------

        actual_route = result["route"]

        actual_method = actual_route.get(
            "method",
            ""
        ).upper()

        actual_path = actual_route.get(
            "path",
            ""
        )

        actual_route_string = (
            f"{actual_method} {actual_path}"
        )

        expected_route = item["route"]

        total_checks += 1

        if actual_route_string == expected_route:
            print("✅ Route")
            passed_checks += 1
        else:
            print("❌ Route")
            print(f"   Expected: {expected_route}")
            print(f"   Actual:   {actual_route_string}")

        # ------------------------------------------------
        # Check controller
        # ------------------------------------------------

        controller = result.get(
            "controller"
        )

        total_checks += 1

        if controller:

            actual_controller_file = controller.get(
                "controller_file"
            )

            actual_controller_function = controller.get(
                "controller_function"
            )

            file_ok = (
                actual_controller_file
                == item["controller_file"]
            )

            function_ok = (
                actual_controller_function
                == item["controller_function"]
            )

            if file_ok and function_ok:
                print("✅ Controller")
                passed_checks += 1
            else:
                print("❌ Controller")

                print(
                    f"   Expected file: "
                    f"{item['controller_file']}"
                )

                print(
                    f"   Actual file:   "
                    f"{actual_controller_file}"
                )

                print(
                    f"   Expected function: "
                    f"{item['controller_function']}"
                )

                print(
                    f"   Actual function:   "
                    f"{actual_controller_function}"
                )

        else:
            print("❌ Controller not found.")

        # ------------------------------------------------
        # Check dependencies
        # ------------------------------------------------

        expected_dependencies = (
            item["expected_dependencies"]
        )

        actual_dependencies = {}

        for dependency in result.get(
            "dependencies",
            []
        ):

            symbol = dependency.get(
                "symbol"
            )

            target_file = dependency.get(
                "target_file"
            )

            actual_dependencies[symbol] = (
                target_file
            )

        for symbol, expected_file in (
            expected_dependencies.items()
        ):

            total_checks += 1

            actual_file = actual_dependencies.get(
                symbol
            )

            if actual_file == expected_file:

                print(
                    f"✅ Dependency: "
                    f"{symbol}"
                )

                passed_checks += 1

            else:

                print(
                    f"❌ Dependency: "
                    f"{symbol}"
                )

                print(
                    f"   Expected: "
                    f"{expected_file}"
                )

                print(
                    f"   Actual:   "
                    f"{actual_file}"
                )

    # ----------------------------------------------------
    # Final score
    # ----------------------------------------------------

    accuracy = (
        passed_checks / total_checks
        if total_checks
        else 0
    )

    print("\n" + "=" * 70)
    print("FINAL FEATURE-FLOW RESULTS")
    print("=" * 70)

    print(
        f"Passed checks: "
        f"{passed_checks}/{total_checks}"
    )

    print(
        f"Feature-flow accuracy: "
        f"{accuracy:.2%}"
    )

    print("=" * 70)


if __name__ == "__main__":
    evaluate()