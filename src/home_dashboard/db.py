from __future__ import annotations

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
import os

DB_URL = os.getenv("HOME_DASHBOARD_DB_URL", "sqlite+aiosqlite:///./home_dashboard.db")

class Base(DeclarativeBase):
    pass

engine = create_async_engine(DB_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:  # type: ignore
        yield session

async def init_db() -> None:
    from . import models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # ensure room column exists (simple additive migration)
        result = await conn.exec_driver_sql("PRAGMA table_info(temperature_readings)")
        cols = [row[1] for row in result.fetchall()]  # second element is name
        if "room" not in cols:
            await conn.exec_driver_sql("ALTER TABLE temperature_readings ADD COLUMN room TEXT NOT NULL DEFAULT 'default'")
