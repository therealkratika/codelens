import re


class CodeTracer:

    def __init__(self, documents, metadatas):

        self.documents = documents
        self.metadatas = metadatas

    def get_file_chunks(self, file_path):

        file_chunks = []

        for document, metadata in zip(
            self.documents,
            self.metadatas
        ):

            if metadata["file"] == file_path:

                file_chunks.append({
                    "document": document,
                    "metadata": metadata
                })

        return file_chunks

    def extract_symbols(self, code):

        symbols = set()

        patterns = [

            # function foo(...)
            r"\bfunction\s+([A-Za-z_$][\w$]*)",

            # const foo = ...
            r"\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=",

            # class Foo
            r"\bclass\s+([A-Za-z_$][\w$]*)",

            # async function foo(...)
            r"\basync\s+function\s+([A-Za-z_$][\w$]*)",

        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                code
            )

            for match in matches:
                symbols.add(match)

        return list(symbols)

    def find_references(self, symbol):

        references = []

        pattern = re.compile(
            r"\b" + re.escape(symbol) + r"\b"
        )

        for document, metadata in zip(
            self.documents,
            self.metadatas
        ):

            if pattern.search(document):

                references.append({
                    "document": document,
                    "metadata": metadata
                })

        return references

    def trace(self, result):

        starting_file = result["metadata"]["file"]

        print(
            f"\nTracing file: {starting_file}"
        )

        # Get all chunks belonging to this file
        file_chunks = self.get_file_chunks(
            starting_file
        )

        # Combine the complete file
        full_code = "\n".join(
            chunk["document"]
            for chunk in file_chunks
        )

        # Extract symbols from complete file
        symbols = self.extract_symbols(
            full_code
        )

        print(
            f"Found symbols: {symbols}"
        )

        related_files = []

        for symbol in symbols:

            references = self.find_references(
                symbol
            )

            for reference in references:

                metadata = reference["metadata"]

                related_files.append({
                    "symbol": symbol,
                    "file": metadata["file"],
                    "start_line": metadata["start_line"],
                    "end_line": metadata["end_line"]
                })

        return related_files