"""Location CRUD and list (admin)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import SessionDep, CurrentUser
from app.core.timezones import get_timezone_options
from app.models.location import Location
from app.models.worker import Worker
from app.models.worker_location import WorkerLocationAssignment
from app.models.user import User
from app.schemas.location import (
    LocationCreate,
    LocationUpdate,
    LocationRead,
    AssignWorkersRequest,
    SendTestRequest,
)
from app.schemas.worker import WorkerRead
from app.services.fcm_service import send_to_topic

router = APIRouter()


@router.get("/timezones")
def list_timezones() -> list[dict[str, str]]:
    """Return timezone options for locations (USA, Pakistan, UTC, etc.)."""
    return get_timezone_options()


def require_company_id(user: User) -> int:
    if not user.company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no company")
    return user.company_id


@router.get("", response_model=list[LocationRead])
async def list_locations(session: SessionDep, current_user: CurrentUser) -> list[LocationRead]:
    company_id = require_company_id(current_user)
    result = await session.execute(select(Location).where(Location.company_id == company_id).order_by(Location.name))
    locations = result.scalars().all()
    return list(locations)


@router.post("", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def create_location(
    data: LocationCreate, session: SessionDep, current_user: CurrentUser
) -> Location:
    company_id = require_company_id(current_user)
    location = Location(company_id=company_id, **data.model_dump())
    session.add(location)
    await session.flush()
    await session.refresh(location)
    return location


# More specific routes first so /{location_id}/workers etc. are not matched by GET /{location_id}
@router.get("/{location_id}/workers", response_model=list[WorkerRead])
async def list_location_workers(
    location_id: int, session: SessionDep, current_user: CurrentUser
) -> list[WorkerRead]:
    """List workers assigned to this location (for testing screen)."""
    company_id = require_company_id(current_user)
    result = await session.execute(
        select(Location).where(Location.id == location_id, Location.company_id == company_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    subq = (
        select(WorkerLocationAssignment.worker_id).where(
            WorkerLocationAssignment.location_id == location_id
        ).distinct()
    )
    result = await session.execute(
        select(Worker).where(Worker.company_id == company_id, Worker.id.in_(subq)).order_by(Worker.id)
    )
    return list(result.scalars().all())


@router.post("/{location_id}/assign-workers", status_code=status.HTTP_200_OK)
async def assign_workers_to_location(
    location_id: int, data: AssignWorkersRequest, session: SessionDep, current_user: CurrentUser
) -> dict:
    """Assign workers to a location (for testing). Workers will receive notifications for this location."""
    company_id = require_company_id(current_user)
    loc_result = await session.execute(
        select(Location).where(Location.id == location_id, Location.company_id == company_id)
    )
    if not loc_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    for worker_id in data.worker_ids:
        w_result = await session.execute(
            select(Worker).where(Worker.id == worker_id, Worker.company_id == company_id)
        )
        if not w_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Worker {worker_id} not found")
        ex_result = await session.execute(
            select(WorkerLocationAssignment).where(
                WorkerLocationAssignment.worker_id == worker_id,
                WorkerLocationAssignment.location_id == location_id,
            )
        )
        if ex_result.scalar_one_or_none():
            continue
        session.add(WorkerLocationAssignment(worker_id=worker_id, location_id=location_id))
    await session.flush()
    return {"assigned": len(data.worker_ids), "location_id": location_id}


@router.post("/{location_id}/send-test", status_code=status.HTTP_200_OK)
async def send_test_notification(
    location_id: int, data: SendTestRequest, session: SessionDep, current_user: CurrentUser
) -> dict:
    """Send a test notification to this location's FCM topic now (all workers subscribed to this location)."""
    company_id = require_company_id(current_user)
    result = await session.execute(
        select(Location).where(Location.id == location_id, Location.company_id == company_id)
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    topic = f"location-{location_id}"
    success, err = send_to_topic(topic, data.title, data.body)
    if not success:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=err or "Failed to send")
    return {"sent": True, "topic": topic, "title": data.title, "body": data.body}


@router.get("/{location_id}", response_model=LocationRead)
async def get_location(
    location_id: int, session: SessionDep, current_user: CurrentUser
) -> LocationRead:
    company_id = require_company_id(current_user)
    result = await session.execute(
        select(Location).where(Location.id == location_id, Location.company_id == company_id)
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return location


@router.patch("/{location_id}", response_model=LocationRead)
async def update_location(
    location_id: int, data: LocationUpdate, session: SessionDep, current_user: CurrentUser
) -> LocationRead:
    company_id = require_company_id(current_user)
    result = await session.execute(
        select(Location).where(Location.id == location_id, Location.company_id == company_id)
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(location, k, v)
    await session.flush()
    await session.refresh(location)
    return location


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int, session: SessionDep, current_user: CurrentUser
) -> None:
    company_id = require_company_id(current_user)
    result = await session.execute(
        select(Location).where(Location.id == location_id, Location.company_id == company_id)
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    await session.delete(location)
    await session.flush()
