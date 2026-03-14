from pydantic import BaseModel


class LocationCreate(BaseModel):
    name: str
    code: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str = "UTC"


class LocationUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None
    is_active: bool | None = None


class LocationRead(BaseModel):
    id: int
    company_id: int
    name: str
    code: str | None
    address: str | None
    latitude: float | None
    longitude: float | None
    timezone: str
    is_active: bool

    model_config = {"from_attributes": True}
