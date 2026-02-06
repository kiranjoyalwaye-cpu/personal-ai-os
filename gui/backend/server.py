"""FastAPI server bootstrap for the Personal AI OS GUI backend."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from gui.backend.agents_api import router as agents_router
from gui.backend.api import router


def create_app() -> FastAPI:
    """Create the FastAPI app and attach routes."""
    app = FastAPI(title="Personal AI OS GUI API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    app.include_router(agents_router)
    return app


app = create_app()
