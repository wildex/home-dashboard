from __future__ import annotations
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from .. import crud, schemas

router = APIRouter(prefix="/api/temperature", tags=["temperature"])

@router.post("/", response_model=schemas.TemperatureReadingOut, status_code=201)
async def add_temperature(payload: schemas.TemperatureReadingCreate, session: AsyncSession = Depends(get_session)):
    reading = await crud.add_temperature(session, payload.value_c, payload.room)
    await session.commit()
    return reading

@router.get("/", response_model=list[schemas.TemperatureReadingOut])
async def recent(session: AsyncSession = Depends(get_session)):
    return await crud.recent_temperatures(session)

@router.delete("/", response_model=schemas.TemperatureClearResult)
async def clear(room: str | None = None, session: AsyncSession = Depends(get_session)):
    deleted = await crud.clear_temperatures(session, room)
    await session.commit()
    return schemas.TemperatureClearResult(deleted=deleted)
