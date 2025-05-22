from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import APIRouter
from fastapi import Depends
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from sqlalchemy.orm import Session
from app.schemas import TokenRequest, TokenResponse 
router = APIRouter()
@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter(User.email == user.email)
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return UserResponse(id=new_user.id, name=new_user.name, email=new_user.email)
@router.post("/login", response_model=TokenResponse)
async def login_user(request: TokenRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token, token_type="bearer")  
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
