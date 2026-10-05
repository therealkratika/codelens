from app.rag.dependency_resolver import DependencyResolver


REPOSITORY_ROOT = "./repositories/Nextja_coding_battle"

resolver = DependencyResolver(
    REPOSITORY_ROOT
)


FILE_PATH = (
    "backend/src/controller/battleController.js"
)

FULL_PATH = (
    f"{REPOSITORY_ROOT}/{FILE_PATH}"
)


with open(
    FULL_PATH,
    "r",
    encoding="utf-8"
) as file:

    code = file.read()


dependencies = resolver.analyze_file(
    FILE_PATH,
    code
)

print("=" * 70)
print("ALL DEPENDENCIES")
print("=" * 70)

for dependency in dependencies:

    print(
        f"{dependency['symbol']}"
        f" → "
        f"{dependency['target_file']}"
        f" "
        f"({dependency['type']})"
    )

print()
print("=" * 70)
print("FUNCTION DEPENDENCIES")
print("=" * 70)

functions_to_test = [
    "createBattle",
    "getBattleQuestions",
    "joinBattle",
]

for function_name in functions_to_test:

    print()
    print(f"{function_name}()")

    results = resolver.trace_function_dependencies(
        FILE_PATH,
        code,
        function_name
    )

    if not results:
        print("  No imported dependencies used.")

    for dependency in results:
        print(
            f"  {dependency['symbol']}"
            f" → "
            f"{dependency['target_file']}"
            f" ({dependency['type']})"
        )