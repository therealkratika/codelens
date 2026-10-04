from app.rag.ast_parser import JavaScriptParser


class CodeAnalyzer:

    def __init__(self):

        self.parser = JavaScriptParser()

    def analyze_file(self, file_path, code):

        result = {
            "file": file_path,
            "imports": [],
            "functions": [],
            "calls": []
        }

        # Currently analyze JavaScript/JSX/TypeScript-like files
        extension = (
            file_path.split(".")[-1]
            .lower()
        )

        supported_extensions = {
            "js",
            "jsx",
            "ts",
            "tsx"
        }

        if extension not in supported_extensions:
            return result

        result["imports"] = (
            self.parser.extract_imports(code)
        )

        result["functions"] = (
            self.parser.extract_functions(code)
        )

        result["calls"] = (
            self.parser.extract_function_calls(code)
        )

        return result