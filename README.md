# Notification Backend & Admin Panel

Backend and Company Admin for a location-based notification system: **Company App** (admin) manages locations and scheduled alerts; **Worker App** (mobile) lets workers select a location and receive FCM notifications for that location.

## Architecture

- **Company Admin**: Manage locations, workers, and scheduled alerts (3–6 times per day). Alerts are sent to **FCM topics** (one topic per location) so all workers at that location get the notification at once (scalable to ~200k users).
- **Worker App** (mobile): Worker logs in with `company_id` + `external_id`, selects current location; mobile app subscribes to FCM topic `location-{id}` and receives broadcasts.
- **Scheduler**: Celery Beat runs every minute and sends FCM messages for schedules whose `send_time` matches the current time in the location’s timezone.

## Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2 (async), PostgreSQL, Redis, Celery, Firebase Admin (FCM)
- **Admin**: React (Vite + TypeScript) in `admin/`; built app served at `/admin`. Fallback: static HTML in `app/static/admin` if React build is not present.
- **Deploy**: Docker Compose (api, db, redis, celery_worker, celery_beat, flower, pgadmin)

## Quick Start (Docker)

```bash
docker compose up -d
# Run migrations (first time)
docker compose exec api python -m alembic upgrade head
# Seed admin user (first time)
docker compose exec api python scripts/seed_admin.py
```

- **API**: http://localhost:8000  
- **API docs**: http://localhost:8000/api/docs  
- **Admin (React)**: http://localhost:8000/admin  
- **Flower** (Celery): http://localhost:5555 (login: `admin` / `admin` unless `FLOWER_AUTH` is set)  
- **Default admin login**: `admin@example.com` / `admin123`

**Celery worker logs** (to see why a task failed):
```bash
docker compose logs -f celery_worker
```
Locations support timezones: set **Timezone** when creating/editing a location. Use IANA names (e.g. `America/New_York`, `Asia/Karachi`). `GET /api/locations/timezones` returns options including USA and Pakistan.

The Docker build includes the React admin (built in the image). For local development of the admin:

```bash
cd admin && npm install && npm run dev
```

Then open http://localhost:5173 (Vite proxies `/api` to the backend). To serve the built admin from FastAPI, run `npm run build` in `admin/` and restart the API; the backend will serve `admin/dist` at `/admin`.

## Local Development (no Docker)

1. PostgreSQL and Redis running locally.
2. Create DB: `createdb notification_db`
3. Copy `.env.example` to `.env` and set `DATABASE_URL`, `DATABASE_URL_SYNC`, `REDIS_URL`.
4. Install: `pip install -r requirements.txt`
5. Migrate: `alembic upgrade head`
6. Seed: `python scripts/seed_admin.py`
7. Run API: `uvicorn app.main:app --reload`
8. Run Celery worker: `celery -A celery_app worker -l info`
9. Run Celery beat: `celery -A celery_app beat -l info`

## API Overview

### Admin (Bearer JWT from `/api/auth/login`)

| Method | Path | Description |
|--------|------|-------------|
| GET/PUT | `/api/companies/me` | Current company |
| GET/POST | `/api/locations` | List / create locations |
| GET/PATCH/DELETE | `/api/locations/{id}` | Get / update / delete location |
| GET/POST | `/api/workers` | List / create workers |
| GET | `/api/workers/{id}` | Get worker |
| POST | `/api/workers/{id}/location` | Set worker’s current location (admin) |
| GET/POST | `/api/schedules` | List / create schedules |
| GET/PATCH/DELETE | `/api/schedules/{id}` | Get / update / delete schedule |

### Worker App (Bearer JWT from `/api/auth/worker/login`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/worker/login` | Body: `company_id`, `external_id`, optional `name`, `phone`, `fcm_token` → JWT |
| GET | `/api/worker/locations` | List locations for worker’s company |
| POST | `/api/worker/location` | Body: `location_id` → set current location, response includes `fcm_topic` |
| GET | `/api/worker/location` | Current location and `fcm_topic` |

### Notifications (FCM)

- Each location has an FCM topic: `location-{location_id}`.
- Worker app subscribes to that topic when the worker selects the location.
- At scheduled times, the backend sends **one** message to the topic; FCM delivers to all subscribers at once (reliable and scalable).

## Environment

See `.env.example`. For production set `SECRET_KEY` and Firebase credentials (`FIREBASE_CREDENTIALS_PATH` or `FIREBASE_CREDENTIALS_BASE64`).

## Scaling Notes

- **DB**: Connection pooling is configured; use read replicas if needed.
- **Celery**: Add more workers for other tasks; one Beat instance is enough for the periodic alert task.
- **FCM**: Topic-based sending means one API call per location per alert, not per user (handles 200k+ users).
