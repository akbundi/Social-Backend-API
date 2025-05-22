from fastapi import FastAPI
from app.routers import users, friends  # example route modules
from fastapi.staticfiles import StaticFiles
from app.core import auth
from app.database import Base, engine

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base  # or wherever your Base is
from app.database import engine
from app.models import Base
from fastapi.responses import FileResponse, RedirectResponse
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
import logging
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:8000"] for tighter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def init_db():
    async with engine.begin() as conn:
          # Optional
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(Base.metadata.drop_all)
# Optional root route
@app.get("/")
def read_index():
    return RedirectResponse(url="/static/index.html")

# Include your actual routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router)
app.include_router(friends.router,tags=["Friends"])
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


for route in app.routes:
    print(route.path)
logging.basicConfig(level=logging.DEBUG)    