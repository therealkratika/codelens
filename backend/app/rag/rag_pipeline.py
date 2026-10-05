
from collections.abc import Callable
import re

from app.rag.retriever import Retriever
from app.rag.context_builder import build_context
from app.rag.feature_flow import FeatureFlowAnalyzer
from app.rag.llm import LLM
from app.rag.query_router import QueryRouter


class RAGPipeline:

    def __init__(self, repository_root):

        print("Initializing CodeLens RAG...")

        self.repository_root = repository_root

        self.retriever = Retriever()
        self.llm = LLM()
        self.query_router = QueryRouter()

        self.feature_flow = FeatureFlowAnalyzer(
            repository_root
        )

        print("CodeLens RAG ready!")

    # FEATURE FLOW DETECTION
    def detect_feature_flows(self, results, question=""):

        del results

        api_file = "frontend/lib/api.ts"
        api_results = self.feature_flow.trace_frontend_api(
            api_file
        )

        question_words = set(
            re.findall(r"[a-z0-9]+", question.lower())
        )

        ignored_words = {
            "a",
            "an",
            "and",
            "does",
            "for",
            "how",
            "is",
            "of",
            "the",
            "to",
            "what",
            "when",
            "where",
            "which",
            "who",
            "why"
        }
        question_words.difference_update(ignored_words)

        scored_apis = []

        for api in api_results:
            function_name = api.get(
                "function",
                ""
            )

            searchable_name = re.sub(
                r"([a-z0-9])([A-Z])",
                r"\1 \2",
                function_name
            ).lower()

            function_words = set(
                re.findall(
                    r"[a-z0-9]+",
                    searchable_name
                )
            )
            function_words.difference_update({
                "get",
                "fetch",
                "request",
                "api"
            })

            relevance = len(
                question_words.intersection(function_words)
            )

            if relevance:
                scored_apis.append((relevance, api))

        if not scored_apis:
            return []

        best_score = max(
            score
            for score, _ in scored_apis
        )

        selected_apis = [
            api
            for score, api in scored_apis
            if score == best_score
        ]

        flows = []

        for api in selected_apis:
            flow = self.feature_flow.trace_api_feature_flow(
                api_file=api_file,
                api_function=api["function"]
            )

            if flow is not None:
                flows.append(flow)

        return flows

    # FIND SERVER / APPLICATION FILE

    def find_server_file(self, route_file):

        import os

        repository_root = self.repository_root

        possible_files = []

        for root, dirs, files in os.walk(repository_root):

            # Ignore unnecessary directories
            dirs[:] = [
                directory
                for directory in dirs
                if directory not in {
                    ".git",
                    "node_modules",
                    "venv",
                    ".venv",
                    "__pycache__",
                    "dist",
                    "build",
                    ".next"
                }
            ]

            for filename in files:

                extension = os.path.splitext(filename)[1].lower()

                if extension not in {
                    ".js",
                    ".jsx",
                    ".ts",
                    ".tsx"
                }:
                    continue

                full_path = os.path.join(
                    root,
                    filename
                )

                try:

                    with open(
                        full_path,
                        "r",
                        encoding="utf-8"
                    ) as file:

                        code = file.read()

                except (UnicodeDecodeError, OSError):

                    continue

                # Check whether this file mounts the route.
                mounts = self.feature_flow.route_analyzer.analyze_mounts(
                    self.relative_repository_path(full_path),
                    code
                )

                if not mounts:
                    continue

                # If the server file contains a mount,
                # consider it a possible application entry point.
                for mount in mounts:

                    if mount.get("router"):

                        possible_files.append(
                            self.relative_repository_path(
                                full_path
                            )
                        )

                        break

        # Prefer common application entry points when several
        # files contain app.use(), without hardcoding one repository.
        preferred_names = {
            "server.js",
            "server.ts",
            "app.js",
            "app.ts",
            "index.js",
            "index.ts",
            "main.js",
            "main.ts"
        }

        for file_path in possible_files:

            filename = file_path.split("/")[-1].lower()

            if filename in preferred_names:

                return file_path

        if possible_files:

            return possible_files[0]

        return None

    # REPOSITORY RELATIVE PATH

    def relative_repository_path(self, absolute_path):

        import os

        return os.path.relpath(
            absolute_path,
            self.repository_root
        ).replace("\\", "/")

    # BUILD FEATURE FLOW CONTEXT

    def build_feature_flow_context(self, feature_flows):

        if not feature_flows:
            return ""

        context_parts = [
            "\n\nFEATURE FLOW:\n"
        ]

        for flow in feature_flows:

            frontend_api = flow.get(
                "frontend_api"
            )

            if frontend_api:
                context_parts.append(
                    "\nFrontend API:\n"
                )
                context_parts.append(
                    f"- Function: "
                    f"{frontend_api.get('function', 'Unknown')}()\n"
                )
                context_parts.append(
                    f"- File: "
                    f"{frontend_api.get('file', 'Unknown')}\n"
                )
                context_parts.append(
                    f"- Line: "
                    f"{frontend_api.get('line', 'Unknown')}\n"
                )
                context_parts.append(
                    f"- Method: "
                    f"{frontend_api.get('method', 'Unknown')}\n"
                )
                context_parts.append(
                    f"- Endpoint: "
                    f"{frontend_api.get('resolved_endpoint', 'Unknown')}\n"
                )

            route = flow.get(
                "route",
                {}
            )

            context_parts.append(
                "\nBackend Route:\n"
            )
            context_parts.append(
                f"- File: "
                f"{route.get('route_file', 'Unknown')}\n"
            )
            context_parts.append(
                f"- Line: "
                f"{route.get('route_line', 'Unknown')}\n"
            )
            context_parts.append(
                f"- Method: "
                f"{route.get('method', 'Unknown')}\n"
            )
            context_parts.append(
                f"- Path: "
                f"{route.get('path', 'Unknown')}\n"
            )
            context_parts.append(
                f"- Handler: "
                f"{route.get('handler', 'Unknown')}\n"
            )

            controller = flow.get("controller")

            context_parts.append(
                "\nController:\n"
            )

            if controller:
                context_parts.append(
                    f"- File: "
                    f"{controller.get('controller_file', 'Unknown')}\n"
                )
                context_parts.append(
                    f"- Function: "
                    f"{controller.get('controller_function', 'Unknown')}\n"
                )
                context_parts.append(
                    f"- Lines: "
                    f"{controller.get('controller_start_line', 'Unknown')}-"
                    f"{controller.get('controller_end_line', 'Unknown')}\n"
                )
            else:
                context_parts.append(
                    "- File: Unknown\n"
                    "- Function: Unknown\n"
                    "- Lines: Unknown\n"
                )

            dependencies = flow.get(
                "dependencies",
                []
            )

            context_parts.append(
                "\nDependencies:\n"
            )

            if dependencies:

                for dependency in dependencies:

                    symbol = dependency.get(
                        "symbol",
                        "Unknown"
                    )

                    target_file = dependency.get(
                        "target_file",
                        "Unknown"
                    )

                    context_parts.append(
                        f"- {symbol} → {target_file}\n"
                    )

            else:

                context_parts.append(
                    "- None detected\n"
                )

            context_parts.append("\n")

        return "".join(context_parts)

    # MAIN RAG PIPELINE

    def answer(
        self,
        question,
        on_text: Callable[[str], None] | None = None
    ):

        print("\nSearching codebase...")

        query_type = self.query_router.classify(
            question
        )

        print(
            f"Query type: {query_type}"
        )

        prefer_code = (
            query_type == "feature_flow"
        )

        # 1. RETRIEVE RELEVANT CODE

        results = self.retriever.retrieve(
            question,
            top_k=5,
            prefer_code=prefer_code
        )
        # 2. BUILD NORMAL CODE CONTEXT

        context = build_context(
            results
        )

        # 3. DETECT FEATURE FLOWS ONLY FOR FLOW QUESTIONS

        feature_flows = []

        if query_type == "feature_flow":
            print(
                "Analyzing feature flows..."
            )

            feature_flows = self.detect_feature_flows(
                results,
                question
            )

            print("\nDEBUG FEATURE FLOWS")
            print("=" * 70)
            for flow in feature_flows:
                print(flow)
            print("=" * 70)

        # 4. ADD FEATURE FLOW CONTEXT

        feature_flow_context = (
            self.build_feature_flow_context(
                feature_flows
            )
        )

        context += feature_flow_context
        # 5. BUILD LLM PROMPT

        prompt = f"""
You are CodeLens, an AI assistant
that understands software repositories.

Answer the user's question using ONLY
the repository context provided below.

IMPORTANT RULES:

1. Do not invent files, functions,
   variables, APIs, dependencies,
   or behavior.

2. If the provided context does not
   contain enough information, say so
   clearly.

3. Explain the answer clearly and
   technically.

4. Mention relevant file names and
   line numbers when explaining code.

5. If FEATURE FLOWS are provided,
   use them to explain how the relevant
   functionality moves through the
   repository.

6. Do not assume a particular
   programming language, framework,
   architecture, directory structure,
   or application domain.

7. Do not create a separate Sources
   section. CodeLens handles sources
   separately.

USER QUESTION:

{question}

REPOSITORY CONTEXT:

{context}

Now answer the user's question.
"""

        # 6. GENERATE ANSWER

        print(
            "Generating answer..."
        )

        answer = self.llm.generate(
            prompt,
            on_text=on_text
        )

        # 7. BUILD SOURCES

        sources = []

        for result in results:

            metadata = result["metadata"]

            sources.append({
                "file": metadata["file"],
                "start_line": metadata["start_line"],
                "end_line": metadata["end_line"],
                "score": result["final_score"]
            })

        # 8. RETURN RESPONSE

        return {
            "answer": answer,
            "sources": sources
        }