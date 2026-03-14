"""Company CRUD (admin)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import SessionDep, CurrentUser
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyRead

router = APIRouter()


def require_company(user: User) -> int:
    if not user.company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no company")
    return user.company_id


@router.get("/me", response_model=CompanyRead)
async def get_my_company(session: SessionDep, current_user: CurrentUser) -> CompanyRead:
    company_id = require_company(current_user)
    result = await session.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return company


@router.put("/me", response_model=CompanyRead)
async def update_my_company(
    data: CompanyCreate, session: SessionDep, current_user: CurrentUser
) -> CompanyRead:
    company_id = require_company(current_user)
    result = await session.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    company.name = data.name
    await session.flush()
    await session.refresh(company)
    return company
