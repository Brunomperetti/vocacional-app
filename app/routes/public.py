"""Rutas públicas generales."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.settings_service import get_donation_url

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Landing principal de vocacional-app."""
    return templates.TemplateResponse(
        "index.html", {"request": request, "donation_url": get_donation_url()}
    )
