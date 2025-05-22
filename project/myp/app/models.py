from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Table
from sqlalchemy.orm import relationship
from app.database import Base
import enum

# Enum for FriendRequest status
class FriendStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"
class FriendRequest(Base):
    __tablename__ = 'friend_requests'
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey('users.id'))
    to_user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum(FriendStatus), default=FriendStatus.pending)
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="sent_requests")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="received_requests")
# User model with relationship to FriendRequest
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))  # Added length
    email = Column(String(120), unique=True, index=True)  # Added length
    password = Column(String(255))  # Added length (safe for hashed passwords)
    bio = Column(String(255), nullable=True)  # Added length (adjust based on your use case)

    # Relationships with FriendRequest (sent and received)
    sent_requests = relationship("FriendRequest", foreign_keys="FriendRequest.from_user_id", back_populates="from_user")
    received_requests = relationship("FriendRequest", foreign_keys="FriendRequest.to_user_id", back_populates="to_user")
    

# FriendRequest model with relationships to User

    # Relationships to User
    
    
    
    
def get_friends(user: User):
    friends = []
    for req in user.sent_requests:
        if req.status == FriendStatus.accepted:
            friends.append(req.to_user)
    for req in user.received_requests:
        if req.status == FriendStatus.accepted:
            friends.append(req.from_user)
    return friends