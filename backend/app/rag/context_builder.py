def build_context(results):

    context_parts = []

    for i, result in enumerate(results):

        metadata = result["metadata"]

        file_path = metadata["file"]
        start_line = metadata["start_line"]
        end_line = metadata["end_line"]

        code = result["document"]

        extension = (
            file_path.split(".")[-1].lower()
        )

        language_map = {
            "js": "javascript",
            "jsx": "javascript",
            "ts": "typescript",
            "tsx": "typescript",
            "py": "python",
            "java": "java",
            "cpp": "cpp",
            "c": "c",
            "html": "html",
            "css": "css",
            "scss": "scss",
            "json": "json",
            "md": "markdown"
        }

        language = language_map.get(
            extension,
            "text"
        )

        context_parts.append(
            f"""
SOURCE {i + 1}

File: {file_path}
Lines: {start_line}-{end_line}

```{language}
{code}
```
"""
        )

    return "\n".join(context_parts)
