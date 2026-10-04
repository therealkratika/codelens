from app.rag.import_resolver import ImportResolver


REPOSITORY_ROOT = "./repositories/Nextja_coding_battle"

resolver = ImportResolver(REPOSITORY_ROOT)


tests = [
    (
        "frontend/components/battle/CreateBattleForm.tsx",
        "../../lib/api",
    ),
    (
        "frontend/components/battle/useBattleRoom.ts",
        "../../lib/api",
    ),
    (
        "backend/src/controller/battleController.js",
        "../utils/generateRoomCode.js",
    ),
    (
        "backend/src/controller/battleController.js",
        "../model/battle.js",
    ),
]


print("=" * 70)
print("IMPORT RESOLVER TEST")
print("=" * 70)


for current_file, import_source in tests:

    result = resolver.resolve(
        current_file,
        import_source
    )

    print("\nCurrent file:")
    print(current_file)

    print("Import:")
    print(import_source)

    print("Resolved:")
    print(result)

    print("-" * 70)