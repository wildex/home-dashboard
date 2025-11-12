from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime

class ApplianceCreate(BaseModel):
    name: str = Field(min_length=1)
    cleaning_interval_days: int | None = Field(default=None, ge=1)

class ApplianceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    cleaning_interval_days: int | None
    created_at: datetime

class CleaningTaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    appliance_id: int
    due_date: date
    completed: bool
    completed_at: datetime | None

class CleaningTaskWithApplianceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    due_date: date
    completed: bool
    completed_at: datetime | None
    appliance: ApplianceOut

class CleaningTaskComplete(BaseModel):
    completed: bool

class TemperatureReadingCreate(BaseModel):
    value_c: float
    room: str | None = Field(default=None, min_length=1)

class TemperatureReadingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    recorded_at: datetime
    value_c: float
    room: str

class DashboardData(BaseModel):
    due_tasks: list[CleaningTaskWithApplianceOut]
    recent_temps: list[TemperatureReadingOut]
    recent_temps_by_room: dict[str, list[TemperatureReadingOut]]

class ApplianceIntervalUpdate(BaseModel):
    cleaning_interval_days: int | None = Field(default=None, ge=1)

class BulkDeleteAppliancesRequest(BaseModel):
    ids: list[int] = Field(min_length=1)

class BulkDeleteAppliancesResult(BaseModel):
    deleted: int

class TemperatureClearResult(BaseModel):
    deleted: int
