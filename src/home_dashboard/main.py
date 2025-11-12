from __future__ import annotations
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from .db import get_session, init_db, SessionLocal
from . import crud, schemas
from .routers import appliances, temperature, tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    auto_seed = os.getenv("HOME_DASHBOARD_AUTO_SEED_DEFAULTS", "true").lower() in {"1","true","yes"}
    async with SessionLocal() as session:  # type: ignore
        await crud.ensure_seed_defaults(session, auto_seed)
        await session.commit()
    yield

def create_app() -> FastAPI:
    app = FastAPI(title="Home Dashboard API", lifespan=lifespan)

    # CORS for React dev
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(appliances.router)
    app.include_router(temperature.router)
    app.include_router(tasks.router)

    @app.get("/api/dashboard", response_model=schemas.DashboardData)
    async def dashboard(session: AsyncSession = Depends(get_session)):
        due = await crud.list_due_tasks(session)
        temps = await crud.recent_temperatures(session, limit=200)
        grouped: dict[str, list[schemas.TemperatureReadingOut]] = {}
        for r in temps:
            out = schemas.TemperatureReadingOut.model_validate(r)
            grouped.setdefault(out.room, []).append(out)
        return schemas.DashboardData(
            due_tasks=[schemas.CleaningTaskWithApplianceOut.model_validate(t) for t in due],
            recent_temps=[schemas.TemperatureReadingOut.model_validate(r) for r in temps],
            recent_temps_by_room=grouped,
        )

    return app

app = create_app()
