"""Punto de entrada de FastAPI para vocacional-app."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routes import admin, public, results, test

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="vocacional-app",
    description="Plataforma online de orientación vocacional con scoring RIASEC.",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(public.router)
app.include_router(test.router)
app.include_router(results.router)
app.include_router(admin.router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Endpoint simple para monitoreo de disponibilidad."""
    return {"status": "ok"}
