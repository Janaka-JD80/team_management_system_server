import pytest
import pytest_asyncio
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Test Database setup
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:TestPassw0rd_123!@localhost:5432/test_db")
engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=False, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_signup(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/signup",
        json={"user_email": "test@example.com", "password": "password123", "full_name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sub" in data
    assert "exp" in data
    
    # Check for httponly cookie
    cookie = response.cookies.get("access_token")
    assert cookie is not None

@pytest.mark.asyncio
async def test_login(async_client: AsyncClient):
    # Setup user
    await async_client.post(
        "/api/v1/auth/signup",
        json={"user_email": "test@example.com", "password": "password123", "full_name": "Test User"}
    )
    
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"user_email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "sub" in data
    assert "exp" in data
    
    cookie = response.cookies.get("access_token")
    assert cookie is not None

@pytest.mark.asyncio
async def test_login_invalid(async_client: AsyncClient):
    # Setup user
    await async_client.post(
        "/api/v1/auth/signup",
        json={"user_email": "test@example.com", "password": "password123", "full_name": "Test User"}
    )
    
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"user_email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.cookies.get("access_token") is None
