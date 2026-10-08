import re
from collections.abc import Iterable, Iterator

# Detect important code structures

FUNCTION_PATTERNS = [
    # function name() {}
    re.compile(
        r"^\s*(?:export\s+)?(?:async\s+)?function\s+"
        r"([A-Za-z_$][\w$]*)\s*\("
    ),

    # const name = () => {}
    re.compile(
        r"^\s*(?:export\s+)?(?:const|let|var)\s+"
        r"([A-Za-z_$][\w$]*)\s*=\s*"
        r"(?:async\s*)?\("
    ),

    # const name = function() {}
    re.compile(
        r"^\s*(?:export\s+)?(?:const|let|var)\s+"
        r"([A-Za-z_$][\w$]*)\s*=\s*function"
    ),

    # methodName() {}
    re.compile(
        r"^\s*(?:async\s+)?"
        r"([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*\{"
    ),
]


CLASS_PATTERN = re.compile(
    r"^\s*(?:export\s+default\s+|export\s+)?"
    r"class\s+([A-Za-z_$][\w$]*)"
)


# Detect opening brace

def count_braces(line):
    """
    Count opening and closing braces.

    This is a lightweight approximation.
    It is not a full JavaScript parser.
    """

    opening = line.count("{")
    closing = line.count("}")

    return opening - closing


# Find logical code structures

def find_code_structures(lines):
    """
    Find functions and classes in a JavaScript/TypeScript file.

    Returns:

    [
        {
            "name": "joinRoom",
            "type": "function",
            "start_line": 10,
            "end_line": 35
        }
    ]
    """

    structures = []

    i = 0

    while i < len(lines):

        line = lines[i]

        structure_type = None
        structure_name = None

        # Check class

        class_match = CLASS_PATTERN.match(line)

        if class_match:

            structure_type = "class"
            structure_name = class_match.group(1)

        else:

            # Check functions

            for pattern in FUNCTION_PATTERNS:

                match = pattern.match(line)

                if match:

                    structure_type = "function"
                    structure_name = match.group(1)

                    break
        # If structure found
        if structure_type:

            start = i

            brace_balance = 0
            found_opening_brace = False

            j = i

            while j < len(lines):

                brace_change = count_braces(lines[j])

                if "{" in lines[j]:
                    found_opening_brace = True

                brace_balance += brace_change

                # Structure is complete
                if (
                    found_opening_brace
                    and brace_balance <= 0
                ):
                    break

                j += 1

            end = min(
                j,
                len(lines) - 1
            )

            structures.append({
                "name": structure_name,
                "type": structure_type,
                "start_line": start + 1,
                "end_line": end + 1
            })

            i = end + 1

        else:

            i += 1

    return structures

# Create code-aware chunks

def chunk_code_file(
    document,
    max_lines=80
):

    content = document["content"]
    file_path = document["file"]

    lines = content.splitlines()

    structures = find_code_structures(lines)

    chunks = []
    # If no structures were detected
    if not structures:

        return chunk_document(
            document,
            chunk_size=50,
            overlap=10
        )
    # Create chunks from structures
    for structure in structures:

        start = structure["start_line"] - 1
        end = structure["end_line"]

        structure_lines = lines[start:end]

        # Very large function/class
        if len(structure_lines) > max_lines:

            sub_document = {
                "file": file_path,
                "content": "\n".join(
                    structure_lines
                )
            }

            sub_chunks = chunk_document(
                sub_document,
                chunk_size=max_lines,
                overlap=10
            )

            for sub_chunk in sub_chunks:

                sub_chunk["start_line"] += start
                sub_chunk["end_line"] += start

                sub_chunk["name"] = structure["name"]
                sub_chunk["type"] = structure["type"]

                chunks.append(sub_chunk)

        else:

            chunks.append({
                "content": "\n".join(
                    structure_lines
                ),
                "file": file_path,
                "start_line": structure["start_line"],
                "end_line": structure["end_line"],
                "name": structure["name"],
                "type": structure["type"]
            })

    return chunks

# Existing line-based chunking

def chunk_document(
    document,
    chunk_size=50,
    overlap=10
):

    content = document["content"]
    file_path = document["file"]

    lines = content.splitlines()

    chunks = []

    start = 0

    while start < len(lines):

        end = min(
            start + chunk_size,
            len(lines)
        )

        chunk_content = "\n".join(
            lines[start:end]
        )

        chunks.append({
            "content": chunk_content,
            "file": file_path,
            "start_line": start + 1,
            "end_line": end
        })

        start += chunk_size - overlap

    return chunks


# ---------------------------------------------------------
# Chunk complete repository
# ---------------------------------------------------------

def iter_document_chunks(
    documents: Iterable[dict[str, str]],
) -> Iterator[dict]:

    for document in documents:

        file_path = document["file"]

        extension = (
            file_path
            .split(".")[-1]
            .lower()
        )

        # JavaScript / TypeScript
        if extension in {
            "js",
            "jsx",
            "ts",
            "tsx"
        }:

            chunks = chunk_code_file(
                document
            )

        # Other languages
        else:

            chunks = chunk_document(
                document
            )

        yield from chunks


def chunk_documents(documents):
    return list(iter_document_chunks(documents))