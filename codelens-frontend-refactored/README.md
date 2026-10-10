# CodeLens frontend — refactored

## Structure
This package follows the requested organization: `api/`, `assets/`, `components/` split by responsibility, `pages/`, `hooks/`, `context/`, `utils/`, and `styles/`.

## Install
Copy the contents into your existing `frontend/` directory (back up first). If preserving your current `package.json`, install the router:
```bash
npm install react-router-dom
```
If using the included `package.json`, run `npm install`.

Create `.env`:
```env
VITE_API_URL=http://localhost:8000
```

Run the backend in one terminal:
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```
Run the frontend in another:
```bash
cd frontend
npm run dev
```

## Confirmed existing backend integration
- `GET /`
- `GET /api/repository/saved`
- `GET /api/repository/status`
- `POST /api/repository/import` with `{ "repo_url": "..." }`
- `GET /api/repository/import/{job_id}`
- `POST /api/repository/activate` with `{ "repository_path": "..." }`
- `POST /api/chat` with `{ "question": "..." }`
- `GET /api/architecture/flows`
- `GET /api/architecture/graph`

## Honest feature boundaries
Architecture loads the backend's feature-flow and code-graph endpoints. Code Explorer uses `/api/chat` with a targeted prompt. Indexed Chunks displays aggregate `files`/`chunks` metadata from saved repositories and uses chat for an explanation of indexing. The backend also provides file-tree and file-content endpoints; the UI does not fabricate individual chunk records.
