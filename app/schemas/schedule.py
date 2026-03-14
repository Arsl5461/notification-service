from datetime import time
from pydantic import BaseModel


class ScheduleCreate(BaseModel):
    location_id: int
    name: str
    message_title: str
    message_body: str
    send_time: time  # e.g. "09:00" in location's timezone


class ScheduleUpdate(BaseModel):
    name: str | None = None
    message_title: str | None = None
    message_body: str | None = None
    send_time: time | None = None
    is_active: bool | None = None


class ScheduleRead(BaseModel):
    id: int
    location_id: int
    name: str
    message_title: str
    message_body: str
    send_time: time
    is_active: bool

    model_config = {"from_attributes": True}
