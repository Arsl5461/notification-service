"""FastAPI dependencies (auth, db session)."""
from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.worker import Worker
from app.core.security import decode_payload

security = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db():
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    session: SessionDep,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials
    payload = decode_payload(token)
    if not payload or payload.get("type") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        user_id = int(sub)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
    return user


async def get_current_worker(
    session: SessionDep,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> Worker:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = credentials.credentials
    payload = decode_payload(token)
    if not payload or payload.get("type") != "worker":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        worker_id = int(sub)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    result = await session.execute(select(Worker).where(Worker.id == worker_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Worker not found")
    return worker


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentWorker = Annotated[Worker, Depends(get_current_worker)]
