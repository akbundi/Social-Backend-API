
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/friends", tags=["Friends"])


@router.post("/request", response_model=schemas.FriendRequestOut)
async def send_friend_request(
    request_data: schemas.FriendRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if request_data.to_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")

    existing = await db.execute(
        select(models.FriendRequest).where(
            (models.FriendRequest.from_user_id == current_user.id) &
            (models.FriendRequest.to_user_id == request_data.to_user_id)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Friend request already sent")

    new_request = models.FriendRequest(
        from_user_id=current_user.id,
        to_user_id=request_data.to_user_id,
        status=models.FriendStatus.pending
    )
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    return new_request


@router.post("/respond/{request_id}", response_model=schemas.FriendRequestOut)
async def respond_to_friend_request(
    request_id: int,
    action: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(select(models.FriendRequest).where(models.FriendRequest.id == request_id))
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request.to_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if action == "accept":
        request.status = models.FriendStatus.accepted
    elif action == "reject":
        request.status = models.FriendStatus.rejected
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    await db.commit()
    await db.refresh(request)
    return request


@router.get("/my-friends", response_model=list[schemas.UserOut])
async def get_my_friends(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(
        select(models.FriendRequest).where(
            ((models.FriendRequest.from_user_id == current_user.id) |
             (models.FriendRequest.to_user_id == current_user.id)) &
            (models.FriendRequest.status == models.FriendStatus.accepted)
        )
    )
    friend_requests = result.scalars().all()

    friend_ids = [
        req.to_user_id if req.from_user_id == current_user.id else req.from_user_id
        for req in friend_requests
    ]

    if not friend_ids:
        return []

    result = await db.execute(select(models.User).where(models.User.id.in_(friend_ids)))
    friends = result.scalars().all()
    return friends