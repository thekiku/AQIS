import asyncio
from contextlib import suppress
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from src.config.scoring import REFRESH_SECONDS
from src.db.db import SessionLocal, init_db
from src.routes.queue_api import router as queue_router
from src.services.queue_service import aqis_service


def create_app() -> FastAPI:
    app = FastAPI(
        title="Adaptive Queue Intelligence System",
        version="1.0.0",
        description="AQIS backend with heap-based lazy updates and versioning",
    )
    app.include_router(queue_router)
    dashboard_path = Path(__file__).resolve().parent / "web" / "index.html"

    async def refresh_loop() -> None:
        while True:
            await asyncio.sleep(REFRESH_SECONDS)
            db = SessionLocal()
            try:
                aqis_service.refresh_scores(db)
            finally:
                db.close()

    @app.on_event("startup")
    async def startup_event() -> None:
        init_db()
        db = SessionLocal()
        try:
            aqis_service.bootstrap_from_db(db)
        finally:
            db.close()

        if REFRESH_SECONDS > 0:
            app.state.refresh_task = asyncio.create_task(refresh_loop())

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        refresh_task = getattr(app.state, "refresh_task", None)
        if refresh_task is None:
            return
        refresh_task.cancel()
        with suppress(asyncio.CancelledError):
            await refresh_task

    @app.get("/", tags=["UI"])
    def ui_dashboard() -> FileResponse:
        return FileResponse(dashboard_path)

    @app.get("/health", tags=["System"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app
