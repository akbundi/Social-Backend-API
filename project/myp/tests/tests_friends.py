import pytest
import uuid
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from app.database import AsyncSessionLocal
from app.models import User, FriendRequest
from app.core.auth import create_access_token

@pytest.fixture
async def create_users():
    async with AsyncSessionLocal() as session:
        # Helper function to create users
        def make_user(name):
            return User(
                name=name,
                email=f"{name.lower()}_{uuid.uuid4().hex[:6]}@example.com",
                password="hashedpassword"
            )

        user1 = make_user("Alice")
        user2 = make_user("Bob")
        user3 = make_user("Charlie")

        session.add_all([user1, user2, user3])
        await session.commit()
        await session.refresh(user1)
        await session.refresh(user2)
        await session.refresh(user3)

        return user1, user2, user3

async def get_auth_header(user_id: int):
    """Generate an Authorization header with a valid JWT token."""
    token = create_access_token({"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_send_friend_request(create_users):
    user1, user2, _ = await create_users
    headers = await get_auth_header(user1.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/friends/request/{user2.id}",
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["msg"] == "Friend request sent"

@pytest.mark.asyncio
async def test_accept_friend_request(create_users):
    sender, receiver, _ = await create_users
    sender_headers = await get_auth_header(sender.id)
    receiver_headers = await get_auth_header(receiver.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Send a friend request
        await client.post(
            f"/friends/request/{receiver.id}", headers=sender_headers
        )

        # Retrieve the friend request ID from DB
        async with AsyncSessionLocal() as session:
            request = await session.execute(
                FriendRequest.__table__.select().where(
                    FriendRequest.from_user_id == sender.id,
                    FriendRequest.to_user_id == receiver.id
                )
            )
            friend_request = request.fetchone()
            request_id = friend_request.id

        # Accept the friend request
        response = await client.post(
            "/friends/respond",
            json={"request_id": request_id, "action": "accept"},
            headers=receiver_headers
        )
        assert response.status_code == 200
        assert response.json()["msg"] == "Friend request accepted"

@pytest.mark.asyncio
async def test_reject_friend_request(create_users):
    sender, receiver, _ = await create_users
    sender_headers = await get_auth_header(sender.id)
    receiver_headers = await get_auth_header(receiver.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Send a friend request
        await client.post(
            f"/friends/request/{receiver.id}", headers=sender_headers
        )

        # Retrieve the friend request ID from DB
        async with AsyncSessionLocal() as session:
            request = await session.execute(
                FriendRequest.__table__.select().where(
                    FriendRequest.from_user_id == sender.id,
                    FriendRequest.to_user_id == receiver.id
                )
            )
            friend_request = request.fetchone()
            request_id = friend_request.id

        # Reject the friend request
        response = await client.post(
            "/friends/respond",
            json={"request_id": request_id, "action": "reject"},
            headers=receiver_headers
        )
        assert response.status_code == 200
        assert response.json()["msg"] == "Friend request rejected"

@pytest.mark.asyncio
async def test_list_friends(create_users):
    user1, user2, _ = await create_users
    headers1 = await get_auth_header(user1.id)
    headers2 = await get_auth_header(user2.id)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Send and accept a friend request
        await client.post(
            f"/friends/request/{user2.id}", headers=headers1
        )

        # Retrieve the friend request ID from DB
        async with AsyncSessionLocal() as session:
            request = await session.execute(
                FriendRequest.__table__.select().where(
                    FriendRequest.from_user_id == user1.id,
                    FriendRequest.to_user_id == user2.id
                )
            )
            friend_request = request.fetchone()
            request_id = friend_request.id

        await client.post(
            "/friends/respond",
            json={"request_id": request_id, "action": "accept"},
            headers=headers2
        )

        # List friends
        response = await client.get("/friends/my-friends", headers=headers1)
        assert response.status_code == 200
        assert any(friend["id"] == user2.id for friend in response.json())
