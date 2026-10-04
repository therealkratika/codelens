from tree_sitter import Language, Parser
import tree_sitter_javascript as javascript


class JavaScriptParser:

    def __init__(self):

        self.language = Language(
            javascript.language()
        )

        self.parser = Parser(
            self.language
        )

    def parse(self, code):

        source = code.encode("utf-8")

        tree = self.parser.parse(source)

        return tree

    def extract_imports(self, code):

        tree = self.parse(code)

        imports = []

        def walk(node):

            if node.type == "import_statement":

                source_node = node.child_by_field_name(
                    "source"
                )

                if source_node:
                    source = code[
                        source_node.start_byte:
                        source_node.end_byte
                    ].strip("\"'")

                    names = []

                    for child in node.named_children:
                        if child.type != "import_clause":
                            continue

                        for subchild in child.named_children:
                            if subchild.type == "identifier":
                                names.append(
                                    code[
                                        subchild.start_byte:
                                        subchild.end_byte
                                    ]
                                )

                            elif subchild.type == "named_imports":
                                for imported in subchild.named_children:
                                    if imported.type != "import_specifier":
                                        continue

                                    name_node = (
                                        imported.child_by_field_name(
                                            "name"
                                        )
                                        or imported.child_by_field_name(
                                            "alias"
                                        )
                                    )

                                    if name_node:
                                        names.append(
                                            code[
                                                name_node.start_byte:
                                                name_node.end_byte
                                            ]
                                        )

                            elif subchild.type == "namespace_import":
                                for imported in subchild.named_children:
                                    if imported.type == "identifier":
                                        names.append(
                                            code[
                                                imported.start_byte:
                                                imported.end_byte
                                            ]
                                        )

                    imports.append({
                        "source": source,
                        "names": names
                    })

            for child in node.named_children:
                walk(child)

        walk(tree.root_node)

        return imports

    def extract_functions(self, code):

        tree = self.parse(code)

        functions = []

        def walk(node):

            # function startBattle() {}
            if node.type == "function_declaration":

                name_node = node.child_by_field_name(
                    "name"
                )

                if name_node:

                    name = code[
                        name_node.start_byte:
                        name_node.end_byte
                    ]

                    functions.append({
                        "name": name,
                        "type": "function",
                        "start_line": (
                            node.start_point[0] + 1
                        ),
                        "end_line": (
                            node.end_point[0] + 1
                        )
                    })

            # const joinBattle = () => {}
            elif node.type == "variable_declarator":

                name_node = node.child_by_field_name(
                    "name"
                )

                value_node = node.child_by_field_name(
                    "value"
                )

                if (
                    name_node
                    and value_node
                    and value_node.type == "arrow_function"
                ):

                    name = code[
                        name_node.start_byte:
                        name_node.end_byte
                    ]

                    functions.append({
                        "name": name,
                        "type": "arrow_function",
                        "start_line": (
                            node.start_point[0] + 1
                        ),
                        "end_line": (
                            node.end_point[0] + 1
                        )
                    })

            for child in node.named_children:
                walk(child)

        walk(tree.root_node)

        return functions

    def extract_function_calls(self, code):

        tree = self.parse(code)

        calls = []

        def walk(node):

            if node.type == "call_expression":

                function_node = (
                    node.child_by_field_name("function")
                )

                if function_node:

                    function_name = code[
                        function_node.start_byte:
                        function_node.end_byte
                    ]

                    calls.append({
                        "name": function_name,
                        "start_line": (
                            node.start_point[0] + 1
                        ),
                        "end_line": (
                            node.end_point[0] + 1
                        )
                    })

            for child in node.children:
                walk(child)

        walk(tree.root_node)

        return calls