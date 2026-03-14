"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.api import auth, locations, workers, schedules, companies, worker_app
from app.db import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


OPENAPI_TAGS = [
    {"name": "auth", "description": "Admin login and worker app login. Use admin JWT for company endpoints, worker JWT for worker endpoints."},
    {"name": "companies", "description": "Company profile (for the logged-in admin user)."},
    {"name": "locations", "description": "Branches, offices, or sites. Each location has an FCM topic for broadcast notifications."},
    {"name": "workers", "description": "Workers/employees. Admin can list and create; worker location selection is also available here for admin use."},
    {"name": "schedules", "description": "Scheduled alerts: time and message per location. Celery Beat sends FCM to the location topic at the configured time."},
    {"name": "worker-app", "description": "Endpoints for the Worker (mobile) app: list locations, select current location, get FCM topic to subscribe to."},
]

app = FastAPI(
    title=settings.app_name,
    description="""
Location-based notification system API.

- **Company Admin**: Log in with email/password, manage locations, workers, and scheduled alerts.
- **Worker App**: Log in with `company_id` + `external_id`, select location, then subscribe to the returned FCM topic to receive alerts.

Notifications are sent via **Firebase Cloud Messaging (FCM) topics** (one topic per location) so all workers at a location receive the same alert at once.
    """.strip(),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=OPENAPI_TAGS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes (under /api for clarity)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(companies.router, prefix="/api/companies", tags=["companies"])
app.include_router(locations.router, prefix="/api/locations", tags=["locations"])
app.include_router(workers.router, prefix="/api/workers", tags=["workers"])
app.include_router(schedules.router, prefix="/api/schedules", tags=["schedules"])
app.include_router(worker_app.router, prefix="/api")

# Serve admin panel: prefer built React app (admin/dist), else static HTML fallback
_project_root = Path(__file__).resolve().parent.parent
_admin_dist = _project_root / "admin" / "dist"
_static_admin = Path(__file__).resolve().parent / "static" / "admin"
if _admin_dist.exists():
    app.mount("/admin", StaticFiles(directory=str(_admin_dist), html=True), name="admin")
else:
    app.mount("/admin", StaticFiles(directory=str(_static_admin), html=True), name="admin")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    """Redirect to API docs."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/docs")
