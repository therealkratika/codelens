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

        # --------------------------------
        # 1. Retrieve relevant code
        # --------------------------------

        print("\nSearching codebase...")

        results = self.retriever.retrieve(
            question,
            top_k=5
        )

        # --------------------------------
        # 2. Build context
        # --------------------------------

        context = build_context(
            results
        )

        # --------------------------------
        # 3. Create prompt
        # --------------------------------

        prompt = f"""
You are CodeLens, an AI assistant
that understands software repositories.

Your job is to answer questions about
the user's codebase.

IMPORTANT RULES:

1. Use ONLY the provided repository
   context to answer.

2. Do NOT invent files, functions,
   APIs, variables, or behavior.

3. If the provided context does not
   contain enough information, clearly
   say that you could not find enough
   information in the codebase.

4. Explain the answer clearly.

5. When referring to code, mention the
   relevant file and line numbers.

6. At the end, provide a Sources section.

USER QUESTION:
{question}

REPOSITORY CONTEXT:
{context}

Now answer the user's question.
"""

        # --------------------------------
        # 4. Send context to LLM
        # --------------------------------

        print("Generating answer...")

        answer = self.llm.generate(
            prompt
        )

        return answer