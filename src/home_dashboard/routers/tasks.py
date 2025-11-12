from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from .. import crud, schemas

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.patch("/{task_id}", response_model=schemas.CleaningTaskOut)
async def update_task(task_id: int, payload: schemas.CleaningTaskComplete, session: AsyncSession = Depends(get_session)):
    task = await crud.complete_task(session, task_id, payload.completed)
    if not task:
        raise HTTPException(404, "Not found")
    await session.commit()
    return task

