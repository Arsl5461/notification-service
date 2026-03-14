"""Authentication (login for admin app and worker app)."""
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.deps import SessionDep, CurrentUser
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.models.worker import Worker
from app.models.company import Company
from app.schemas.auth import LoginRequest, Token, WorkerLoginRequest

router = APIRouter()
settings = get_settings()


@router.post("/login", response_model=Token)
async def login(data: LoginRequest, session: SessionDep) -> Token:
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
    access_token = create_access_token(
        subject=str(user.id),
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        token_type="admin",
    )
    return Token(access_token=access_token)


@router.get("/me")
async def me(current_user: CurrentUser):
    return {"id": current_user.id, "email": current_user.email, "full_name": current_user.full_name, "company_id": current_user.company_id}


@router.post("/worker/login", response_model=Token)
async def worker_login(data: WorkerLoginRequest, session: SessionDep) -> Token:
    """Worker app: register or login with company_id + external_id. Returns JWT for worker endpoints."""
    result = await session.execute(select(Company).where(Company.id == data.company_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    result = await session.execute(
        select(Worker).where(
            Worker.company_id == data.company_id,
            Worker.external_id == data.external_id,
        )
    )
    worker = result.scalar_one_or_none()
    if not worker:
        worker = Worker(
            company_id=data.company_id,
            external_id=data.external_id,
            name=data.name,
            phone=data.phone,
            fcm_token=data.fcm_token,
        )
        session.add(worker)
        await session.flush()
        await session.refresh(worker)
    else:
        if data.fcm_token is not None:
            worker.fcm_token = data.fcm_token
        if data.name is not None:
            worker.name = data.name
        if data.phone is not None:
            worker.phone = data.phone
        await session.flush()
    access_token = create_access_token(
        subject=str(worker.id),
        expires_delta=timedelta(days=30),
        token_type="worker",
    )
    return Token(access_token=access_token)
