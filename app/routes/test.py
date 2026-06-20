"""Rutas iniciales del test vocacional."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/test", tags=["test"])


@router.get("", response_class=HTMLResponse)
async def test_start(request: Request):
    """Pantalla inicial del test vocacional."""
    return templates.TemplateResponse("test_start.html", {"request": request})
