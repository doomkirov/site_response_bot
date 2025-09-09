from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from settings.settings import settings

engine: AsyncEngine = create_async_engine(settings.db_url, echo=True)

async_session_maker: sessionmaker[AsyncSession] = sessionmaker(engine, class_=AsyncSession, # noqa
                                                               expire_on_commit=False)

class Base(DeclarativeBase):
    pass
