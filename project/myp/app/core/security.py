from passlib.context import CryptContext
import bcrypt
import importlib.metadata
version = importlib.metadata.version("bcrypt")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)
