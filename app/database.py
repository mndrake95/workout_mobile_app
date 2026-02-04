from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo = True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()