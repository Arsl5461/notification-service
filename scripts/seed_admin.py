"""Create initial company and admin user. Run once after DB is up."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.config import get_settings
from app.core.security import get_password_hash
from app.db.session import engine
from app.db.base import Base
from app.models.company import Company
from app.models.user import User


async def seed():
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import async_session

    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == "admin@example.com"))
        if result.scalar_one_or_none():
            print("Admin user already exists.")
            return
        company = Company(name="Default Company")
        session.add(company)
        await session.flush()
        user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin",
            is_active=True,
            company_id=company.id,
        )
        session.add(user)
        await session.commit()
        print("Created company and admin user: admin@example.com / admin123")


if __name__ == "__main__":
    asyncio.run(seed())
