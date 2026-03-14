"""Worker app API: list locations, select current location, get FCM topic."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import SessionDep, CurrentWorker
from app.models.location import Location
from app.models.worker_location import WorkerLocationAssignment
from app.schemas.location import LocationRead
from app.schemas.worker import WorkerLocationSelect

router = APIRouter(prefix="/worker", tags=["worker-app"])


@router.get("/locations", response_model=list[LocationRead])
async def list_my_locations(session: SessionDep, current_worker: CurrentWorker) -> list[LocationRead]:
    """List all active locations for the worker's company (to choose where they're working today)."""
    result = await session.execute(
        select(Location).where(
            Location.company_id == current_worker.company_id,
            Location.is_active == True,
        ).order_by(Location.name)
    )
    locations = result.scalars().all()
    return list(locations)


@router.post("/location", status_code=status.HTTP_200_OK)
async def select_my_location(
    data: WorkerLocationSelect, session: SessionDep, current_worker: CurrentWorker
) -> dict:
    """
    Set worker's current location. Returns FCM topic name so the mobile app
    can subscribe to it and receive broadcast notifications for this location.
    """
    result = await session.execute(
        select(Location).where(
            Location.id == data.location_id,
            Location.company_id == current_worker.company_id,
            Location.is_active == True,
        )
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    assignment = WorkerLocationAssignment(
        worker_id=current_worker.id,
        location_id=data.location_id,
    )
    session.add(assignment)
    await session.flush()
    # FCM topic: one topic per location; all workers at that location subscribe.
    # Single send to topic = all subscribers get it at once (scalable).
    topic = f"location-{data.location_id}"
    return {"location_id": data.location_id, "fcm_topic": topic, "message": "Subscribe to this FCM topic to receive alerts."}


@router.get("/location")
async def get_my_current_location(
    session: SessionDep, current_worker: CurrentWorker
) -> dict | None:
    """Get worker's most recently selected location (and its FCM topic)."""
    result = await session.execute(
        select(WorkerLocationAssignment)
        .where(WorkerLocationAssignment.worker_id == current_worker.id)
        .order_by(WorkerLocationAssignment.selected_at.desc())
        .limit(1)
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        return None
    return {
        "location_id": assignment.location_id,
        "fcm_topic": f"location-{assignment.location_id}",
    }
