"""Scheduled alerts (admin CRUD). Sending is done by Celery Beat."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import SessionDep, CurrentUser
from app.models.schedule import Schedule
from app.models.location import Location
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleRead

router = APIRouter()


def require_company_id(user: User) -> int:
    if not user.company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no company")
    return user.company_id


@router.get("", response_model=list[ScheduleRead])
async def list_schedules(
    session: SessionDep,
    current_user: CurrentUser,
    location_id: int | None = None,
) -> list[ScheduleRead]:
    company_id = require_company_id(current_user)
    q = select(Schedule).join(Location).where(Location.company_id == company_id)
    if location_id is not None:
        q = q.where(Schedule.location_id == location_id)
    q = q.order_by(Schedule.location_id, Schedule.send_time)
    result = await session.execute(q)
    schedules = result.scalars().all()
    return list(schedules)


@router.post("", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: ScheduleCreate, session: SessionDep, current_user: CurrentUser
) -> Schedule:
    company_id = require_company_id(current_user)
    result = await session.execute(
        select(Location).where(Location.id == data.location_id, Location.company_id == company_id)
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    schedule = Schedule(location_id=data.location_id, **data.model_dump())
    session.add(schedule)
    await session.flush()
    await session.refresh(schedule)
    return schedule


@router.get("/{schedule_id}", response_model=ScheduleRead)
async def get_schedule(
    schedule_id: int, session: SessionDep, current_user: CurrentUser
) -> ScheduleRead:
    company_id = require_company_id(current_user)
    result = await session.execute(
        select(Schedule).join(Location).where(Schedule.id == schedule_id, Location.company_id == company_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    return schedule


@router.patch("/{schedule_id}", response_model=ScheduleRead)
async def update_schedule(
    schedule_id: int, data: ScheduleUpdate, session: SessionDep, current_user: CurrentUser
) -> ScheduleRead:
    company_id = require_company_id(current_user)
    result = await session.execute(
        select(Schedule).join(Location).where(Schedule.id == schedule_id, Location.company_id == company_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(schedule, k, v)
    await session.flush()
    await session.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int, session: SessionDep, current_user: CurrentUser
) -> None:
    company_id = require_company_id(current_user)
    result = await session.execute(
        select(Schedule).join(Location).where(Schedule.id == schedule_id, Location.company_id == company_id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found")
    await session.delete(schedule)
    await session.flush()
