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

## Honest feature boundaries
Architecture and Code Explorer call the existing `/api/chat` endpoint with targeted prompts. Indexed Chunks displays aggregate `files`/`chunks` metadata from saved repositories and uses chat for an explanation of indexing. The current backend contract provided in the project context does not confirm endpoints for a graph of architecture, raw file browsing, or listing individual chunk records; the UI does not fabricate those records. For actual graph/file/chunk records, add dedicated backend endpoints and then update the matching `api/*Api.js` service.
