from app.rag.retriever import Retriever
from app.rag.context_builder import build_context
from app.rag.llm import LLM


class RAGPipeline:

    def __init__(self):

        print("Initializing CodeLens RAG...")

        self.retriever = Retriever()
        self.llm = LLM()

        print("CodeLens RAG ready!")

    def answer(self, question):

        # 1. Retrieve relevant code

        print("\nSearching codebase...")

        results = self.retriever.retrieve(
            question,
            top_k=5
        )

        
        # 2. Build context

        context = build_context(results)

        # 3. Generate prompt

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

4. Do NOT create a Sources section.
   CodeLens will generate the sources
   separately.

USER QUESTION:
{question}

REPOSITORY CONTEXT:
{context}

Now answer the user's question.
"""
        # 4. Generate answer

        print("Generating answer...")

        answer = self.llm.generate(prompt)

        # 5. Generate trusted sources
        sources = []

        for result in results:

            metadata = result["metadata"]

            sources.append({
                "file": metadata["file"],
                "start_line": metadata["start_line"],
                "end_line": metadata["end_line"],
                "score": result["hybrid_score"]
            })
        # 6. Return answer + sources
        return {
            "answer": answer,
            "sources": sources
        }