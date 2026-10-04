from collections import defaultdict


class CodeGraph:

    def __init__(self):

        self.nodes = {}
        self.edges = []

    def add_file(self, file_path, analysis):

        self.nodes[file_path] = {
            "file": file_path,
            "imports": analysis["imports"],
            "functions": analysis["functions"],
            "calls": analysis["calls"]
        }

    def add_edge(
        self,
        source,
        target,
        relation
    ):

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

    def build_call_edges(self):

        for file_path, node in self.nodes.items():

            for call in node["calls"]:

                call_name = call["name"]

                # Handle calls such as:
                # Question.find
                # Battle.create

                if "." in call_name:

                    object_name = (
                        call_name.split(".")[0]
                    )

                    method_name = (
                        call_name.split(".")[-1]
                    )

                    matches = self.find_function(
                        method_name
                    )

                else:

                    matches = self.find_function(
                        call_name
                    )

                for match in matches:

                    self.add_edge(
                        file_path,
                        match["file"],
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