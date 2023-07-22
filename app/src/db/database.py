from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine


from core.config import SETTINGS

engine = create_async_engine(SETTINGS.SQLALCHEMY_DATABASE_URL, echo=SETTINGS.ORM_ECHO)
engine_sync = create_engine(SETTINGS.SQLALCHEMY_DATABASE_URL_SYNC)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
Base = declarative_base()


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


