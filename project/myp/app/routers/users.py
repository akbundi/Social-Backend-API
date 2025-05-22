from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.hash import bcrypt
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=schemas.UserOut)
async def register_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if user with the email already exists
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash the password
    hashed_password = bcrypt.hash(user.password)

    # Create user instance
    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )
    db.add(new_user)

    # Commit transaction to save to database
    await db.commit()

    # Refresh instance with new data (e.g., id)
    await db.refresh(new_user)

    return new_user


@router.get("/{user_id}", response_model=schemas.UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=schemas.UserOut)
async def update_user(user_id: int, user_update: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user fields
    user.name = user_update.name
    user.email = user_update.email
    user.password = bcrypt.hash(user_update.password)

    # Commit changes
    await db.commit()
    await db.refresh(user)
    return user