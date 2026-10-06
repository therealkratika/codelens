import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    backend_root = Path(__file__).resolve().parent.parent
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

from app.rag.rag_pipeline import RAGPipeline


def main():

    repository_root = "repositories/Nextja_coding_battle"

    rag = RAGPipeline(repository_root)

    flows = rag.detect_feature_flows(
        [],
        "How does a player join a battle?"
    )

    print("\n" + "=" * 70)
    print("FEATURE FLOW FALLBACK TEST")
    print("=" * 70)

    for flow in flows:
        print(flow)

    answer = rag.build_feature_flow_fallback(
        "How does a player join a battle?",
        flows
    )

    print("\n" + "=" * 70)
    print("FALLBACK ANSWER")
    print("=" * 70)
    print(answer)


if __name__ == "__main__":
    main()