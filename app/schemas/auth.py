from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class WorkerLoginRequest(BaseModel):
    """Worker app: identify by company + device/phone. Creates worker if new."""
    company_id: int
    external_id: str  # device id or phone
    name: str | None = None
    phone: str | None = None
    fcm_token: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
