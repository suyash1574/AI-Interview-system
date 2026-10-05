from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.config import settings

engine_kwargs = {
    "echo": getattr(settings, "DB_ECHO", False),
}

# Apply pool sizing for production databases (e.g. Postgres asyncpg)
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": getattr(settings, "DB_POOL_SIZE", 20),
        "max_overflow": getattr(settings, "DB_MAX_OVERFLOW", 10),
        "pool_recycle": getattr(settings, "DB_POOL_RECYCLE", 3600),
        "pool_pre_ping": getattr(settings, "DB_POOL_PRE_PING", True),
    })

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

