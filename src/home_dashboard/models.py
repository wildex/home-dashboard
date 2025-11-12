from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Date, DateTime, Boolean, Float, String
from datetime import datetime, date, timedelta, timezone
from .db import Base

class Appliance(Base):
    __tablename__ = "appliances"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    cleaning_interval_days: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tasks: Mapped[list[CleaningTask]] = relationship(back_populates="appliance", cascade="all, delete-orphan")

class CleaningTask(Base):
    __tablename__ = "cleaning_tasks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appliance_id: Mapped[int] = mapped_column(ForeignKey("appliances.id", ondelete="CASCADE"))
    due_date: Mapped[date]
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    appliance: Mapped[Appliance] = relationship(back_populates="tasks")

class TemperatureReading(Base):
    __tablename__ = "temperature_readings"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    value_c: Mapped[float] = mapped_column(Float)
    room: Mapped[str] = mapped_column(String, default="default", index=True)

class AppMeta(Base):
    __tablename__ = "app_meta"
    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str | None]

# Helper scheduling logic used after appliance creation or task completion
async def ensure_future_task(session, appliance: Appliance) -> CleaningTask | None:
    """Ensure there is one upcoming incomplete task for the appliance.

    Previous logic could produce a new task with the same due_date if the base date
    calculation matched an existing task's due date (e.g., rapid re-completion or
    overlapping scheduling). We now compute the next due date strictly after any
    existing task due dates or the last completion date.
    """
    if not appliance.cleaning_interval_days:
        return None
    from sqlalchemy import select
    # Gather all incomplete tasks ordered by due date
    result = await session.execute(
        select(CleaningTask).where(
            CleaningTask.appliance_id == appliance.id,
            CleaningTask.completed == False  # noqa: E712
        ).order_by(CleaningTask.due_date)
    )
    incomplete = result.scalars().all()
    today = date.today()
    # If there is a future (>= today) incomplete task, reuse it
    future_incomplete = [t for t in incomplete if t.due_date >= today]
    if future_incomplete:
        return future_incomplete[0]

    # Determine a monotonically increasing base date
    last_completed_result = await session.execute(
        select(CleaningTask).where(
            CleaningTask.appliance_id == appliance.id,
            CleaningTask.completed == True  # noqa: E712
        ).order_by(CleaningTask.completed_at.desc())
    )
    last_completed = last_completed_result.scalars().first()

    # Consider latest due date of any task (completed or not) to avoid duplicates
    any_tasks_result = await session.execute(
        select(CleaningTask).where(CleaningTask.appliance_id == appliance.id).order_by(CleaningTask.due_date.desc())
    )
    latest_task = any_tasks_result.scalars().first()

    candidates: list[date] = []
    if last_completed and last_completed.completed_at:
        candidates.append(last_completed.completed_at.date())
    if latest_task:
        candidates.append(latest_task.due_date)
    if not candidates:
        candidates.append(appliance.created_at.date())

    base_date = max(candidates)
    # Next due must be strictly after base_date
    due = base_date + timedelta(days=appliance.cleaning_interval_days)

    new_task = CleaningTask(appliance_id=appliance.id, due_date=due)
    session.add(new_task)
    await session.flush()
    return new_task
