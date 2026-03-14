from datetime import datetime
from pydantic import BaseModel


class WorkerCreate(BaseModel):
    name: str | None = None
    phone: str | None = None
    external_id: str | None = None


class WorkerRead(BaseModel):
    id: int
    company_id: int
    external_id: str | None
    name: str | None
    phone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerLocationSelect(BaseModel):
    """Worker app: select which location they're at (mobile sends this)."""
    location_id: int
