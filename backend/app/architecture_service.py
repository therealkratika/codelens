import os
from collections import defaultdict
from typing import Dict, List, Any, Optional

from app.rag.feature_flow import FeatureFlowAnalyzer
from app.rag.code_graph import CodeGraph
from app.rag.code_analyzer import CodeAnalyzer
from app.rag.vector_store import VectorStore


class ArchitectureService:
    def __init__(self, repository_path: str):
        self.repository_path = repository_path
        self.analyzer = FeatureFlowAnalyzer(repository_path)
        self.code_analyzer = CodeAnalyzer()
        self.vector_store = VectorStore(repository_path)
        self._flows_cache: Optional[List[Dict[str, Any]]] = None
        self._graph_cache: Optional[Dict[str, Any]] = None

    def get_feature_flows(self) -> List[Dict[str, Any]]:
        if self._flows_cache is not None:
            return self._flows_cache

        api_files = []
        ignored = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".next"}
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if d not in ignored]
            for f in files:
                if f.lower() in {"api.js", "api.ts", "client.js", "client.ts"}:
                    rel = os.path.relpath(os.path.join(root, f), self.repository_path).replace(os.sep, "/")
                    api_files.append(rel)

        route_files = []
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if d not in ignored]
            for f in files:
                if f.endswith((".js", ".ts")) and ("route" in f.lower() or "routes" in root.lower()):
                    rel = os.path.relpath(os.path.join(root, f), self.repository_path).replace(os.sep, "/")
                    route_files.append(rel)

        server_file = None
        for candidate in ["backend/server.js", "server.js", "backend/src/server.js", "src/server.js"]:
            if os.path.exists(os.path.join(self.repository_path, candidate)):
                server_file = candidate
                break

        flows = []
        for api_file in api_files:
            api_results = self.analyzer.trace_frontend_api(api_file)
            for api in api_results:
                matched_flow = None
                for rf in route_files:
                    sf = server_file or self.analyzer._find_server_file(rf)
                    if not sf:
                        continue
                    flow = self.analyzer.trace_route(
                        route_file=rf,
                        server_file=sf,
                        handler=api.get("function", "")
                    )
                    if flow and self.analyzer.match_api_to_route(api, flow):
                        flow["frontend_api"] = api
                        flow["id"] = f"{api_file}:{api['function']}"
                        flow["name"] = api["function"]
                        matched_flow = flow
                        break

                if matched_flow:
                    flows.append(matched_flow)
                else:
                    flows.append({
                        "id": f"{api_file}:{api['function']}",
                        "name": api["function"],
                        "frontend_api": api,
                        "route": None,
                        "controller": None,
                        "dependencies": []
                    })

        self._flows_cache = flows
        return flows

    def get_code_graph(self) -> Dict[str, Any]:
        if self._graph_cache is not None:
            return self._graph_cache

        graph = CodeGraph(self.repository_path)
        data = self.vector_store.collection.get(include=["documents", "metadatas"])
        files = defaultdict(list)
        for doc, meta in zip(data["documents"], data["metadatas"]):
            files[meta["file"]].append({"doc": doc, "start": meta.get("start_line", 0)})

        for fp, chunks in files.items():
            if not any(fp.endswith(ext) for ext in [".js", ".jsx", ".ts", ".tsx"]):
                continue
            chunks.sort(key=lambda x: x["start"])
            code = "\n".join(c["doc"] for c in chunks)
            analysis = self.code_analyzer.analyze_file(fp, code)
            graph.add_file(fp, analysis)

        graph.build_import_edges()
        graph.build_call_edges()

        # Build clean node representations
        formatted_nodes = []
        for file_path, node_data in graph.nodes.items():
            formatted_nodes.append({
                "id": file_path,
                "file": file_path,
                "imports": node_data.get("imports", []),
                "functions": node_data.get("functions", []),
                "calls": node_data.get("calls", []),
                "imports_count": len(node_data.get("imports", [])),
                "functions_count": len(node_data.get("functions", [])),
                "calls_count": len(node_data.get("calls", []))
            })

        result = {
            "summary": graph.summary(),
            "nodes": formatted_nodes,
            "edges": graph.edges
        }
        self._graph_cache = result
        return result
