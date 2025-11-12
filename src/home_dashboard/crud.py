from __future__ import annotations
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone, date, timedelta
from . import models

async def create_appliance(session: AsyncSession, name: str, cleaning_interval_days: int | None):
    existing = await session.execute(select(models.Appliance).where(models.Appliance.name == name))
    appliance = existing.scalars().first()
    if appliance:
        # update interval if provided and different
        if cleaning_interval_days and appliance.cleaning_interval_days != cleaning_interval_days:
            appliance.cleaning_interval_days = cleaning_interval_days
        return appliance
    appliance = models.Appliance(name=name, cleaning_interval_days=cleaning_interval_days)
    session.add(appliance)
    await session.flush()
    await models.ensure_future_task(session, appliance)
    return appliance

async def list_appliances(session: AsyncSession):
    result = await session.execute(select(models.Appliance).order_by(models.Appliance.created_at.desc()))
    return result.scalars().all()

async def get_appliance(session: AsyncSession, appliance_id: int):
    result = await session.execute(select(models.Appliance).where(models.Appliance.id == appliance_id))
    return result.scalars().first()

async def list_tasks_for_appliance(session: AsyncSession, appliance_id: int):
    result = await session.execute(select(models.CleaningTask).where(models.CleaningTask.appliance_id == appliance_id).order_by(models.CleaningTask.due_date))
    return result.scalars().all()

async def update_appliance_interval(session: AsyncSession, appliance_id: int, new_interval: int | None):
    appliance = await get_appliance(session, appliance_id)
    if not appliance:
        return None
    old_interval = appliance.cleaning_interval_days
    appliance.cleaning_interval_days = new_interval
    # remove all future incomplete tasks regardless of interval value
    future_tasks_stmt = select(models.CleaningTask).where(
        models.CleaningTask.appliance_id == appliance_id,
        models.CleaningTask.completed == False,  # noqa: E712
        models.CleaningTask.due_date >= date.today(),
    )
    result = await session.execute(future_tasks_stmt)
    for t in result.scalars().all():
        await session.delete(t)
    await session.flush()
    if new_interval:
        # schedule from today (more intuitive after interval change)
        due = date.today() + timedelta(days=new_interval)
        new_task = models.CleaningTask(appliance_id=appliance.id, due_date=due)
        session.add(new_task)
        await session.flush()
    return appliance

async def complete_task(session: AsyncSession, task_id: int, completed: bool):
    result = await session.execute(select(models.CleaningTask).where(models.CleaningTask.id == task_id))
    task = result.scalars().first()
    if not task:
        return None
    task.completed = completed
    task.completed_at = datetime.now(timezone.utc) if completed else None
    if completed:
        appliance_result = await session.execute(select(models.Appliance).where(models.Appliance.id == task.appliance_id))
        appliance = appliance_result.scalars().first()
        if appliance:
            await models.ensure_future_task(session, appliance)
    await session.flush()
    return task

async def list_due_tasks(session: AsyncSession):
    from datetime import date
    today = date.today()
    stmt = select(models.CleaningTask).options(selectinload(models.CleaningTask.appliance)).where(models.CleaningTask.completed == False).order_by(models.CleaningTask.due_date)  # noqa: E712
    result = await session.execute(stmt)
    tasks = result.scalars().all()
    return [t for t in tasks if t.due_date <= today]

async def add_temperature(session: AsyncSession, value_c: float, room: str | None):
    reading = models.TemperatureReading(value_c=value_c, room=room or "default")
    session.add(reading)
    await session.flush()
    return reading

async def recent_temperatures(session: AsyncSession, limit: int = 200):
    result = await session.execute(select(models.TemperatureReading).order_by(models.TemperatureReading.recorded_at.desc()).limit(limit))
    readings = list(reversed(result.scalars().all()))
    return readings

async def clear_temperatures(session: AsyncSession, room: str | None):
    stmt = delete(models.TemperatureReading)
    if room:
        from sqlalchemy import and_
        stmt = stmt.where(models.TemperatureReading.room == room)
    result = await session.execute(stmt)
    await session.flush()
    return result.rowcount or 0

async def seed_default_appliances(session: AsyncSession):
    """Idempotently create a starter set of appliances if they don't already exist.
    Uses AppMeta sentinel key 'seed_defaults_done'.
    """
    sentinel_key = "seed_defaults_done"
    meta_q = await session.execute(select(models.AppMeta).where(models.AppMeta.key == sentinel_key))
    if meta_q.scalars().first():
        return []
    defaults = [
        ("Dishwasher", 30),
        ("Cat Fountain", 7),
        ("Washer", 14),
        ("Fridge Water Filter", 90),
        ("HVAC Filter", 60),
        ("Humidifier", 7),
        ("Litter Box Deep Clean", 14),
    ]
    created = []
    for name, interval in defaults:
        existing = await session.execute(select(models.Appliance).where(models.Appliance.name == name))
        if existing.scalars().first():
            continue
        created.append(await create_appliance(session, name, interval))
    # set sentinel
    session.add(models.AppMeta(key=sentinel_key, value="1"))
    await session.flush()
    return created

async def ensure_seed_defaults(session: AsyncSession, auto: bool):
    if not auto:
        return False
    created = await seed_default_appliances(session)
    return bool(created)
