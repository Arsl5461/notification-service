"""Location CRUD and list (admin)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import SessionDep, CurrentUser
from app.models.location import Location
from app.models.user import User
from app.schemas.location import LocationCreate, LocationUpdate, LocationRead

router = APIRouter()


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
