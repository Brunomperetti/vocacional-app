"""Punto de entrada de FastAPI para Vocación360."""

import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base, engine
from app import models  # noqa: F401 - registra modelos ORM antes de crear tablas
from app.routes import admin, public, results, test, testimonials

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=os.getenv("APP_NAME", "Vocación360"),
    description="Plataforma online de orientación vocacional con scoring RIASEC.",
    version="0.1.0",
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "dev-session-secret-change-me"),
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(public.router)
app.include_router(test.router)
app.include_router(results.router)
app.include_router(testimonials.router)
app.include_router(admin.router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Endpoint simple para monitoreo de disponibilidad."""
    return {"status": "ok"}
