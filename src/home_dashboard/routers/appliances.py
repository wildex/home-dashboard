from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from .. import crud
from .. import schemas

router = APIRouter(prefix="/api/appliances", tags=["appliances"])

@router.get("/", response_model=list[schemas.ApplianceOut])
async def list_appliances(session: AsyncSession = Depends(get_session)):
    return await crud.list_appliances(session)

@router.post("/", response_model=schemas.ApplianceOut, status_code=201)
async def create_appliance(payload: schemas.ApplianceCreate, session: AsyncSession = Depends(get_session)):
    appliance = await crud.create_appliance(session, payload.name, payload.cleaning_interval_days)
    await session.commit()
    return appliance

@router.get("/{appliance_id}", response_model=schemas.ApplianceOut)
async def get_appliance(appliance_id: int, session: AsyncSession = Depends(get_session)):
    appliance = await crud.get_appliance(session, appliance_id)
    if not appliance:
        raise HTTPException(404, "Not found")
    return appliance

@router.patch("/{appliance_id}/interval", response_model=schemas.ApplianceOut)
async def update_interval(appliance_id: int, payload: schemas.ApplianceIntervalUpdate, session: AsyncSession = Depends(get_session)):
    appliance = await crud.update_appliance_interval(session, appliance_id, payload.cleaning_interval_days)
    if not appliance:
        raise HTTPException(404, "Not found")
    await session.commit()
    return appliance

@router.post("/bulk-delete", response_model=schemas.BulkDeleteAppliancesResult)
async def bulk_delete(payload: schemas.BulkDeleteAppliancesRequest, session: AsyncSession = Depends(get_session)):
    deleted = 0
    for id_ in set(payload.ids):
        appliance = await crud.get_appliance(session, id_)
        if appliance:
            await session.delete(appliance)
            deleted += 1
    await session.commit()
    return schemas.BulkDeleteAppliancesResult(deleted=deleted)

@router.get("/{appliance_id}/tasks", response_model=list[schemas.CleaningTaskOut])
async def tasks_for_appliance(appliance_id: int, session: AsyncSession = Depends(get_session)):
    appliance = await crud.get_appliance(session, appliance_id)
    if not appliance:
        raise HTTPException(404, "Not found")
    return await crud.list_tasks_for_appliance(session, appliance_id)
