# Home Dashboard

FastAPI JSON API + (planned) React frontend for household maintenance tasks and environment tracking.

## Features
- JSON API for appliances (create, list, interval update, bulk delete)
- Cleaning task scheduling & completion
- Temperature readings ingestion
- Dashboard aggregate endpoint `/api/dashboard`
- Idempotent default seeding (disable via `HOME_DASHBOARD_AUTO_SEED_DEFAULTS=false`)

## Tech Stack
- Python 3.12 / FastAPI / SQLAlchemy (async) / Pydantic v2
- SQLite (aiosqlite) for persistence
- React frontend (to be added) consuming JSON endpoints

## Install & Run API
```bash
pip install -e '.[dev]'
uvicorn home_dashboard.main:app --reload
```
API root examples:
```bash
curl http://127.0.0.1:8000/api/appliances/
curl http://127.0.0.1:8000/api/dashboard
```

## Endpoints
- `GET /api/appliances/` list appliances
- `POST /api/appliances/` create `{name, cleaning_interval_days?}`
- `PATCH /api/appliances/{id}/interval` update/unschedule interval
- `POST /api/appliances/bulk-delete` `{ids:[...]}`
- `GET /api/appliances/{id}/tasks` list tasks
- `PATCH /api/tasks/{task_id}` complete task
- `POST /api/temperature/` add reading
- `GET /api/temperature/` recent readings
- `GET /api/dashboard` aggregate overdue tasks + recent temps

## Seeding
Auto-seeds defaults once using an AppMeta sentinel. Disable:
```bash
export HOME_DASHBOARD_AUTO_SEED_DEFAULTS=false
```
Manual seed (idempotent):
```bash
curl -X POST http://127.0.0.1:8000/appliances/seed -I
```

## Testing
```bash
pytest -q
```

## Lint
```bash
ruff check .
```

## React Frontend (next steps)
Scaffold with Vite or CRA, consume the API above, implement polling/websocket for live temperature updates.
