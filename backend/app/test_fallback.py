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