from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.core.settings import DATABASE_URL, DB_NAME

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def _server_url() -> str:
    """从 DATABASE_URL 中剥离库名，得到仅含 host/user/password 的服务地址。"""
    parsed = urlparse(DATABASE_URL)
    return f"{parsed.scheme}://{parsed.netloc}"


async def _create_database_if_not_exists():
    temp_engine = create_async_engine(_server_url(), echo=False)
    try:
        async with temp_engine.begin() as conn:
            await conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
    except Exception as e:
        print(f"创建数据库失败: {e}")
        raise
    finally:
        await temp_engine.dispose()


async def init_db():
    await _create_database_if_not_exists()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    await engine.dispose()
