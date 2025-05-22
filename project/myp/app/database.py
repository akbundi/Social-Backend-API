from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
# Creating async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Creating session factory for async operations
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as db:
        yield db
