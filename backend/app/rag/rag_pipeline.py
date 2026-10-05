from app.rag.retriever import Retriever
from app.rag.context_builder import build_context
from app.rag.feature_flow import FeatureFlowAnalyzer
from app.rag.llm import LLM


class RAGPipeline:

    def __init__(self):

        print("Initializing CodeLens RAG...")

        self.retriever = Retriever()
        self.llm = LLM()
        self.feature_flow = FeatureFlowAnalyzer(
            "./repositories/Nextja_coding_battle"
        )

        print("CodeLens RAG ready!")

    def answer(self, question):

        print("\nSearching codebase...")

        results = self.retriever.retrieve(
            question,
            top_k=5
        )

        context = build_context(results)

        prompt = f"""
You are CodeLens, an AI assistant
that understands software repositories.

Answer the user's question using ONLY
the repository context provided below.

IMPORTANT RULES:

1. Do not invent files, functions,
   variables, APIs, or behavior.

2. If the context does not contain
   enough information, say so clearly.

3. Explain the answer clearly and
   technically.

4. Mention relevant file names and
   line numbers when explaining the code.

5. Do not create a separate Sources
   section. CodeLens handles sources
   separately.

USER QUESTION:

{question}

REPOSITORY CONTEXT:

{context}

Now answer the user's question.
"""

        print("Generating answer...")

        answer = self.llm.generate(prompt)

        sources = []

        for result in results:

            metadata = result["metadata"]

            sources.append({
                "file": metadata["file"],
                "start_line": metadata["start_line"],
                "end_line": metadata["end_line"],
                "score": result["final_score"]
            })

        return {
            "answer": answer,
            "sources": sources
        }