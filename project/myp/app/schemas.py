from pydantic import BaseModel, EmailStr
from typing import Optional
from pydantic import ConfigDict

# ------------------- User Schemas -------------------

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    bio: Optional[str] = None

    model_config: ConfigDict = {
        'from_attributes': True
    }

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config: ConfigDict = {
        'from_attributes': True
    }

# ------------------- Auth Schemas -------------------

class TokenRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ------------------- Friend Request Schemas -------------------

class FriendRequestCreate(BaseModel):
    to_user_id: int

class FriendRequestAction(BaseModel):
    request_id: int
    action: str  # 'accept' or 'reject'

class FriendRequestOut(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    status: str

    model_config: ConfigDict = {
        'from_attributes': True
    }

# ------------------- Friend Association Schemas -------------------

class FriendAssociationBase(BaseModel):
    from_user_id: int
    to_user_id: int
    status: Optional[str] = None

class FriendAssociationCreate(FriendAssociationBase):
    pass

class FriendAssociationUpdate(BaseModel):
    status: Optional[str] = None

class FriendAssociationOut(FriendAssociationBase):
    id: int

    model_config: ConfigDict = {
        'from_attributes': True
    }