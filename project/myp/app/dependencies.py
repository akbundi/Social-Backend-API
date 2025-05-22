from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models, database
from app.core import auth
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session
from sqlalchemy.future import select
from jose import jwt, JWTError
from app.database import get_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = auth.decode_token(token)
        # Perform async query to fetch the user
        result = await db.execute(select(models.User).filter(models.User.id == payload.get("sub")))
        user = result.scalar_one_or_none()  # Get the single user or None
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")