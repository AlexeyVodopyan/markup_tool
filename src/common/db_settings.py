# stdlib
from asyncio import current_task

# thirdparty
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

# project
from common.db_config import pg_settings

SQLALCHEMY_URL = URL.create(
    drivername="postgresql+asyncpg",
    host=pg_settings.host,
    username=pg_settings.user,
    password=pg_settings.password,
    port=pg_settings.port,
    database=pg_settings.db,
)

engine = create_async_engine(SQLALCHEMY_URL)

Session = async_scoped_session(
    sessionmaker(bind=engine, class_=AsyncSession), scopefunc=current_task
)


async def get_session():
    session = Session()
    try:
        yield session
    finally:
        await session.close()
