"""Workers: admin CRUD + worker app endpoints (select location, register device)."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import SessionDep, CurrentUser
from app.models.worker import Worker
from app.models.location import Location
from app.models.worker_location import WorkerLocationAssignment
from app.models.user import User
from app.schemas.worker import WorkerCreate, WorkerRead, WorkerLocationSelect

router = APIRouter()


def require_company_id(user: User) -> int:
    if not user.company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no company")
    return user.company_id


# ---- Admin: list/create workers (optionally by location) ----
@router.get("", response_model=list[WorkerRead])
async def list_workers(
    session: SessionDep,
    current_user: CurrentUser,
    location_id: int | None = Query(None, description="Filter by location (workers currently at this location)"),
) -> list[WorkerRead]:
    company_id = require_company_id(current_user)
    if location_id:
        # Workers who have selected this location (latest assignment)
        subq = (
            select(WorkerLocationAssignment.worker_id)
            .where(WorkerLocationAssignment.location_id == location_id)
            .distinct()
        )
        result = await session.execute(
            select(Worker).where(Worker.company_id == company_id, Worker.id.in_(subq)).order_by(Worker.id)
        )
    else:
        result = await session.execute(select(Worker).where(Worker.company_id == company_id).order_by(Worker.id))
    workers = result.scalars().all()
    return list(workers)


@router.post("", response_model=WorkerRead, status_code=status.HTTP_201_CREATED)
async def create_worker(
    data: WorkerCreate, session: SessionDep, current_user: CurrentUser
) -> Worker:
    company_id = require_company_id(current_user)
    worker = Worker(company_id=company_id, **data.model_dump())
    session.add(worker)
    await session.flush()
    await session.refresh(worker)
    return worker


@router.get("/{worker_id}", response_model=WorkerRead)
async def get_worker(
    worker_id: int, session: SessionDep, current_user: CurrentUser
) -> WorkerRead:
    company_id = require_company_id(current_user)
    result = await session.execute(
        select(Worker).where(Worker.id == worker_id, Worker.company_id == company_id)
    )
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")
    return worker


# ---- Worker app: select current location (mobile calls this) ----
# Mobile app can use API key or JWT for worker; for simplicity we use worker_id + optional API key
# In production you'd have worker-specific JWT or API key.
@router.post("/{worker_id}/location", status_code=status.HTTP_204_NO_CONTENT)
async def worker_select_location(
    worker_id: int,
    data: WorkerLocationSelect,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    """Admin or worker: set worker's current location (for receiving alerts)."""
    company_id = require_company_id(current_user)
    result = await session.execute(
        select(Worker).where(Worker.id == worker_id, Worker.company_id == company_id)
    )
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not found")
    result = await session.execute(
        select(Location).where(Location.id == data.location_id, Location.company_id == company_id)
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    assignment = WorkerLocationAssignment(worker_id=worker_id, location_id=data.location_id)
    session.add(assignment)
    await session.flush()
    return None
