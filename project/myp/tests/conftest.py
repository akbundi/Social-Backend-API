import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.core.security import get_password_hash  # Adjust path as needed
#import pytest_asyncio
from main import app
from httpx import AsyncClient
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client
@pytest.mark.fixture
async def create_users(async_session: AsyncSession):
    # Use unique emails or clean up before inserting
    await async_session.execute("DELETE FROM users")  # Clean slate

    user1 = User(name="Alice", email="alice1@example.com", password=get_password_hash("password1"))
    user2 = User(name="Bob", email="bob1@example.com", password=get_password_hash("password2"))
    user3 = User(name="Charlie", email="charlie1@example.com", password=get_password_hash("password3"))

    async_session.add_all([user1, user2, user3])
    await async_session.commit()

    # Refresh to ensure IDs are populated
    await async_session.refresh(user1)
    await async_session.refresh(user2)
    await async_session.refresh(user3)

    return user1, user2, user3
