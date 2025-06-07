import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (create_async_engine,
                                    async_sessionmaker, AsyncSession)

from app.main import app
from app.db.database import Base, get_session

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine_test = create_async_engine(DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine_test, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture()
async def async_session(prepare_database):
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture()
async def client(async_session: AsyncSession):
    async def override_get_session():
        yield async_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
