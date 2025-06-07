from sqlalchemy.ext.asyncio import (create_async_engine,
                                    AsyncSession, async_sessionmaker)
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

DATABASE_URL = "sqlite+aiosqlite:///./weather.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

Base = declarative_base()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
