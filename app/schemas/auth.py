from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Use admin@example.com / admin123 to create the default admin (if missing) and log in."""

    model_config = {"json_schema_extra": {"examples": [{"email": "admin@example.com", "password": "admin123"}]}}

    email: EmailStr = Field(description="Admin email")
    password: str = Field(description="Password")


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
