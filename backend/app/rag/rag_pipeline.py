
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

    def find_api_files(self):
        import os

        api_files = []
        ignored_dirs = {
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            "dist",
            "build",
            ".next",
            "coverage",
            ".cache",
            "out",
            "target",
        }
        api_file_names = {
            "api.js",
            "api.jsx",
            "api.ts",
            "api.tsx",
            "client.js",
            "client.ts",
            "http.js",
            "http.ts",
        }

        for root, dirs, files in os.walk(self.repository_root):
            dirs[:] = [
                directory
                for directory in dirs
                if directory not in ignored_dirs
            ]

            for filename in files:
                if filename.lower() not in api_file_names:
                    continue

                full_path = os.path.join(
                    root,
                    filename
                )
                relative_path = os.path.relpath(
                    full_path,
                    self.repository_root
                )

                api_files.append(
                    relative_path.replace(
                        os.sep,
                        "/"
                    )
                )

        return api_files

    # FEATURE FLOW DETECTION
    def detect_feature_flows(self, results, question=""):

        del results

        api_files = self.find_api_files()

        if not api_files:
            return []

        api_results = []

        for api_file in api_files:
            results = self.feature_flow.trace_frontend_api(
                api_file
            )

            for api in results:
                api["_api_file"] = api_file
                api_results.append(api)

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
            "why",
            "can",
            "could",
            "would",
            "should",
            "someone",
            "something",
        }
        question_words.difference_update(
            ignored_words
        )

        # Words that commonly describe API intent.
        intent_words = {
            "create": {
                "create",
                "created",
                "creating",
                "creation",
                "start",
                "starts"
            },
            "join": {
                "join",
                "joining",
                "enter",
                "enters",
                "entered",
                "room"
            },
            "leave": {
                "leave",
                "leaving",
                "exit",
                "remove",
                "removed"
            },
            "get": {
                "get",
                "fetch",
                "retrieve",
                "load",
                "loads",
                "fetching"
            },
            "submit": {
                "submit",
                "submitting",
                "submission",
                "send",
                "sending"
            },
            "update": {
                "update",
                "updating",
                "edit",
                "change",
                "modify"
            },
            "delete": {
                "delete",
                "deleting",
                "remove",
                "removing"
            },
        }

        scored_apis = []

        for api in api_results:
            function_name = api.get(
                "function",
                ""
            )
            endpoint = api.get(
                "resolved_endpoint",
                ""
            )
            method = api.get(
                "method",
                ""
            )

            # Convert camelCase into separate words.
            searchable_function = re.sub(
                r"([a-z0-9])([A-Z])",
                r"\1 \2",
                function_name
            ).lower()

            function_words = set(
                re.findall(
                    r"[a-z0-9]+",
                    searchable_function
                )
            )
            endpoint_words = set(
                re.findall(
                    r"[a-z0-9]+",
                    endpoint.lower()
                )
            )

            matched_intents = {
                intent
                for intent, words in intent_words.items()
                if question_words.intersection(words)
                and function_words.intersection(words)
            }

            intent_score = len(matched_intents) * 5

            function_overlap = question_words.intersection(
                function_words - {
                    "get",
                    "fetch",
                    "request",
                    "api"
                }
            )
            endpoint_overlap = question_words.intersection(
                endpoint_words - {
                    "https",
                    "http",
                    "api",
                    "com",
                    "org",
                    "net",
                    "onrender"
                }
            )

            relevance = (
                intent_score
                + len(function_overlap) * 2
                + len(endpoint_overlap)
            )

            # GET is the conventional HTTP verb for read/fetch APIs.
            if (
                "get" in matched_intents
                and method.upper() == "GET"
            ):
                relevance += 1

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
                api_file=api["_api_file"],
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

    def build_feature_flow_fallback(
        self,
        question,
        feature_flows
    ):

        del question

        if not feature_flows:
            return (
                "CodeLens could not generate an answer because "
                "the LLM is currently unavailable."
            )

        lines = [
            "The LLM is currently unavailable, but "
            "CodeLens successfully traced the feature flow.\n"
        ]

        for flow in feature_flows:
            frontend_api = flow.get("frontend_api")

            if frontend_api:
                lines.append(
                    f"Frontend: "
                    f"{frontend_api.get('function', 'Unknown')}() "
                    f"at {frontend_api.get('file', 'Unknown')}:"
                    f"{frontend_api.get('line', 'Unknown')}"
                )
                lines.append(
                    f"HTTP: "
                    f"{frontend_api.get('method', 'Unknown')} "
                    f"{frontend_api.get('resolved_endpoint', 'Unknown')}"
                )

            route = flow.get("route")

            if route:
                lines.append(
                    f"Backend Route: "
                    f"{route.get('method', 'Unknown')} "
                    f"{route.get('path', 'Unknown')}"
                )
                lines.append(
                    f"at {route.get('route_file', 'Unknown')}:"
                    f"{route.get('route_line', 'Unknown')}"
                )

            controller = flow.get("controller")

            if controller:
                lines.append(
                    f"Controller: "
                    f"{controller.get('controller_function', 'Unknown')}()"
                )
                lines.append(
                    f"at {controller.get('controller_file', 'Unknown')}:"
                    f"{controller.get('controller_start_line', 'Unknown')}-"
                    f"{controller.get('controller_end_line', 'Unknown')}"
                )

            dependencies = flow.get("dependencies", [])

            if dependencies:
                lines.append("Dependencies:")

                for dependency in dependencies:
                    lines.append(
                        f"- {dependency.get('symbol', 'Unknown')} → "
                        f"{dependency.get('target_file', 'Unknown')}"
                    )

        return "\n".join(lines)

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

        try:
            answer = self.llm.generate(
                prompt,
                on_text=on_text
            )
        except RuntimeError as error:
            print(
                f"\nLLM unavailable: {error}",
                flush=True
            )

            if feature_flows:
                answer = self.build_feature_flow_fallback(
                    question,
                    feature_flows
                )
                if on_text is not None:
                    on_text(answer)
            else:
                raise

        # 7. BUILD SOURCES

        sources = []

        # Sources from normal retrieval
        for result in results:

            metadata = result["metadata"]

            sources.append({
                "file": metadata["file"],
                "start_line": metadata["start_line"],
                "end_line": metadata["end_line"],
                "score": result["final_score"]
            })

        # Add sources discovered through feature-flow tracing
        if feature_flows:
            for flow in feature_flows:
                frontend_api = flow.get("frontend_api")

                if frontend_api:
                    sources.append({
                        "file": frontend_api.get("file"),
                        "start_line": frontend_api.get("line"),
                        "end_line": frontend_api.get("line")
                    })

                route = flow.get("route")

                if route:
                    sources.append({
                        "file": route.get("route_file"),
                        "start_line": route.get("route_line"),
                        "end_line": route.get("route_line")
                    })

                    if route.get("mount_file"):
                        sources.append({
                            "file": route.get("mount_file"),
                            "start_line": route.get("mount_line"),
                            "end_line": route.get("mount_line")
                        })

                controller = flow.get("controller")

                if controller:
                    sources.append({
                        "file": controller.get("controller_file"),
                        "start_line": controller.get(
                            "controller_start_line"
                        ),
                        "end_line": controller.get(
                            "controller_end_line"
                        )
                    })

                for dependency in flow.get("dependencies", []):
                    target_file = dependency.get("target_file")

                    if target_file:
                        sources.append({
                            "file": target_file,
                            "start_line": None,
                            "end_line": None
                        })

        unique_sources = []
        seen_sources = set()

        for source in sources:
            key = (
                source.get("file"),
                source.get("start_line"),
                source.get("end_line")
            )

            if key in seen_sources:
                continue

            seen_sources.add(key)
            unique_sources.append(source)

        sources = unique_sources

        # 8. RETURN RESPONSE

        return {
            "answer": answer,
            "sources": sources
        }