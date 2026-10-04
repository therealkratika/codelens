from app.rag.import_resolver import ImportResolver


class CodeGraph:

    def __init__(self, repository_root):
        self.nodes = {}
        self.edges = []

        self.import_resolver = ImportResolver(
            repository_root
        )

    def add_file(self, file_path, analysis):

        self.nodes[file_path] = {
            "file": file_path,
            "imports": analysis["imports"],
            "functions": analysis["functions"],
            "calls": analysis["calls"]
        }

    def add_edge(self, source, target, relation):

        self.edges.append({
            "source": source,
            "target": target,
            "relation": relation
        })

    def find_function(self, name):

        matches = []

        for file_path, node in self.nodes.items():

            for function in node["functions"]:

                if function["name"] == name:

                    matches.append({
                        "file": file_path,
                        "function": function
                    })

        return matches

    def build_import_edges(self):

        for file_path, node in self.nodes.items():

            for import_data in node["imports"]:

                import_source = import_data["source"]

                target_file = self.import_resolver.resolve(
                    file_path,
                    import_source
                )

                if target_file is None:
                    continue

                self.add_edge(
                    file_path,
                    target_file,
                    "imports"
                )

    def build_call_edges(self):

        for file_path, node in self.nodes.items():

            imported_symbols = {}

            # Resolve imported functions
            for import_data in node["imports"]:

                import_source = import_data["source"]

                target_file = self.import_resolver.resolve(
                    file_path,
                    import_source
                )

                if target_file is None:
                    continue

                for name in import_data["names"]:

                    imported_symbols[name] = target_file

            # Process calls
            for call in node["calls"]:

                call_name = call["name"]

                # Ignore object methods such as:
                # console.log()
                # Question.find()
                # socket.emit()
                if "." in call_name:
                    continue

                # Only create call edges for explicitly imported functions.
                if call_name not in imported_symbols:
                    continue

                target_file = imported_symbols[call_name]

                # Never create self-edges.
                if target_file == file_path:
                    continue

                self.add_edge(
                    file_path,
                    target_file,
                    f"calls:{call_name}"
                )

    def get_edges_for_file(self, file_path):

        return [
            edge
            for edge in self.edges
            if edge["source"] == file_path
        ]

    def summary(self):

        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges)
        }