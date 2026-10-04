def chunk_document(document, chunk_size=50, overlap=10):

    content = document["content"]
    file_path = document["file"]

    lines = content.splitlines()

    chunks = []

    start = 0

    while start < len(lines):

        end = min(start + chunk_size, len(lines))

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


def chunk_documents(documents):

    all_chunks = []

    for document in documents:

        chunks = chunk_document(document)

        all_chunks.extend(chunks)

    return all_chunks