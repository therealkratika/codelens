# CodeLens

CodeLens is a local codebase intelligence workspace. Import a GitHub repository, ask questions about its implementation, inspect detected API flows and dependencies, and browse source files with indexed chunk references.

## Features

- Import and index public GitHub repositories.
- Switch between previously imported repositories without cloning them again.
- Ask codebase questions with Gemini-powered answers and source references.
- Search indexed code using local embeddings, ChromaDB vector search, BM25 keyword search, and reranking.
- Explore detected API routes, feature flows, dependency graphs, and repository files.
- Generate repository-specific suggested questions.

## Architecture

```text
frontend/  Next.js App Router, React, TypeScript
    |
    | /api/* rewrite (NEXT_PUBLIC_API_URL)
    v
backend/   FastAPI
    |
    +-- GitPython       Clone public GitHub repositories
    +-- loader/chunker  Select and split supported source files
    +-- sentence-transformers / all-MiniLM-L6-v2
    +-- ChromaDB        Persist embeddings and code chunks
    +-- rank-bm25       Keyword retrieval
    +-- Gemini API      Generate chat answers
```

Repository checkouts are stored under `backend/repositories/`. ChromaDB data is stored under `backend/chroma_db/`. The selected repository and saved repository list are stored in `backend/repository_state.json`. These are local development files and should not be committed.

## Requirements

- Python 3.10 or newer (Python 3.14 has been used in development).
- Node.js 20.9 or newer and npm.
- A Gemini API key for repository Q&A.
- Internet access for cloning GitHub repositories, downloading the local embedding model on first use, and calling Gemini.

## Setup

### 1. Configure the Gemini API key

Create `backend/.env`:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
```

Get a key from [Google AI Studio](https://aistudio.google.com/app/apikey). Do not commit `.env` files or share the key. The backend loads `GEMINI_API_KEY` from its environment.

### 2. Install and start the backend

From the repository root:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API listens at `http://127.0.0.1:8000`. The root endpoint returns a basic health/status response. FastAPI's interactive API documentation is available at `http://127.0.0.1:8000/docs`.

The embedding model is downloaded the first time the backend initializes and is then cached by the model library. Initial startup and repository indexing can take a while, especially on CPU-only machines.

### 3. Configure and start the frontend

In a second terminal, create `frontend/.env.local`:

```dotenv
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Then run:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`. Keep the backend running while using the frontend. Restart the Next.js development server after changing `.env.local`.

## Using CodeLens

1. Open the frontend and enter a public GitHub repository URL, such as `https://github.com/owner/repository`.
2. Wait for cloning, file loading, chunking, embedding, and indexing to finish.
3. Ask questions in Code Chat or explore the Overview, Architecture, and File Explorer sections.
4. Use **Switch Repo** to select a saved repository or import another one. The last imported/selected repository is restored when the backend restarts, as long as its checkout still exists.

The import screen currently accepts GitHub repository URLs. Private repositories are not supported by the frontend's URL validation and may also require Git credentials that are not configured for the backend.

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Backend status |
| `POST` | `/api/repository/import` | Clone or reactivate and index a GitHub repository |
| `GET` | `/api/repository/status` | Active repository status |
| `GET` | `/api/repository` | Active repository details |
| `GET` | `/api/repository/saved` | List saved repositories |
| `POST` | `/api/repository/activate` | Activate a saved repository |
| `GET` | `/api/repository/suggestions` | Get suggested questions for the active repository |
| `POST` | `/api/chat` | Ask a question about the active repository |
| `GET` | `/api/architecture/flows` | Get detected API and feature flows |
| `GET` | `/api/architecture/graph` | Get the code dependency graph |
| `GET` | `/api/files/tree` | Get the repository file tree |
| `GET` | `/api/files/content?path=...` | Get a file and its indexed chunk metadata |

## Indexing and retrieval details

- Supported indexed file extensions are Python, JavaScript, JSX, TypeScript, TSX, Java, C/C++, HTML, CSS/SCSS, JSON, and Markdown.
- Dependency/build output directories such as `.git`, `node_modules`, `.venv`, `dist`, and `.next` are excluded.
- Repository text is chunked and embedded locally with `all-MiniLM-L6-v2`.
- Chunks are embedded and written to ChromaDB in batches of 256.
- Repository vector collections are separated by checkout path.
- Chat retrieval combines vector search, BM25 keyword search, and reranking before sending relevant context to Gemini.
- JavaScript/TypeScript AST parsing and flow detection are heuristic and may not recognize every framework, language, or coding style.

## Gemini quota and API exhaustion

Gemini is used to generate chat responses; it is not used to calculate repository embeddings. The current backend model is configured in `backend/app/rag/llm.py`. The client streams answers and retries selected timeouts and temporary service/rate-limit errors up to three attempts. Retries do not provide more quota.

If Gemini returns a quota or rate-limit error (commonly HTTP 429), chat may fail even though the repository was cloned and indexed successfully. Check:

1. That `GEMINI_API_KEY` is valid and belongs to the intended Google AI Studio project.
2. The project's model access, billing status, request/token quotas, and rate limits.
3. Whether the quota window has reset before retrying.
4. That the configured model is available to the project.

Increasing the API quota or enabling billing may incur charges. Review Google's current pricing and quota rules before doing so. A missing key or unavailable model can also prevent the backend from initializing the RAG pipeline.

## Troubleshooting

### The frontend reports that it cannot connect

- Confirm the backend is running at the URL in `frontend/.env.local`.
- Ensure `NEXT_PUBLIC_API_URL` has no `/api` suffix; Next.js adds the `/api/...` route.
- Restart the frontend after changing `.env.local`.

### Repository import fails

- Confirm the URL is a public GitHub repository URL and GitHub is reachable.
- Check the backend terminal for the full import exception.
- Ensure the repository contains at least one non-empty file with a supported extension.
- Large repositories can take significant time and disk space. Indexing is batched, but local embedding still requires memory and compute.
- If a previous import failed partway through, retry it; the vector collection is cleared before a fresh indexing run.

### A saved repository is missing or does not restore

- Saved repository state is local to `backend/repository_state.json`.
- The corresponding clone must still exist under `backend/repositories/`.
- If the checkout or state file was removed, import the repository URL again.

### Chat fails after indexing

- Check the Gemini API key, model access, network connection, and quota as described above.
- Backend logs include the underlying Gemini error. Avoid publishing logs that contain credentials or other sensitive environment data.

## Development checks

Frontend:

```bash
cd frontend
npm run build
npm run lint
```

Backend syntax check:

```bash
cd backend
python -m py_compile app/main.py app/repository_service.py app/rag/rag_pipeline.py
```

Backend files named `test_*.py` currently include runnable smoke/demo scripts as well as analysis helpers; they are not all pytest-discoverable test functions. For example, run the AST parser demo from `backend/` with:

```bash
python -m app.test_ast
```

## Current limitations

- Repository clones, saved repository metadata, and ChromaDB are local to one backend machine. This is not yet a multi-user or horizontally scaled deployment design.
- The repository metadata registry is a JSON file, not a transactional database.
- Private GitHub repository authentication is not implemented in the UI.
- Supported source extensions and ignored directories are explicitly listed in `backend/app/ingestion/loader.py`; binary assets and other languages are not indexed.
- AST-based route/feature-flow analysis is heuristic. Missing or incomplete flow data does not necessarily mean the repository has no such code.
- Gemini quota exhaustion, model availability, network errors, and service outages can interrupt chat independently of local indexing.
- Re-importing a repository currently performs indexing again; there is no incremental Git-change indexing.

## Future enhancements

- Incremental indexing that updates only changed or deleted files.
- Background import jobs with progress reporting, cancellation, and resumable failures.
- Better language coverage and parser-backed framework-aware route/flow analysis.
- Optional private repository support using secure, short-lived GitHub credentials or an app integration.
- Replace the JSON registry with SQLite or PostgreSQL when concurrent users or multiple backend instances are needed.
- Add multi-user workspaces, access controls, and isolated per-user repository metadata.
- Add model selection, configurable Gemini retry/backoff, and graceful model-provider alternatives.
- Cache and reuse compatible embedding/reranking models; support configurable CPU/GPU inference.
- Add automated backend unit/API tests and CI checks for import, repository switching, retrieval, and quota failures.
- Add production deployment guidance, observability, usage/cost tracking, and data-retention controls.

## Data and privacy

Repository source is cloned and indexed on the machine running the backend. Relevant retrieved code context and the user's question are sent to Gemini when generating an answer. Do not import code or submit prompts unless you are permitted to process that material with the configured services. Remove local repository and ChromaDB data when it should no longer be retained.
