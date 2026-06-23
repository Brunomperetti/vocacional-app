"""Rutas públicas generales."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.settings_service import get_app_name, get_public_template_context

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["get_app_name"] = get_app_name
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Landing principal de Vocación360."""
    return templates.TemplateResponse(
        "index.html", get_public_template_context(request=request, page="landing")
    )


@router.get("/privacidad", response_class=HTMLResponse)
async def privacy(request: Request):
    """Página pública de privacidad y uso de datos."""
    return templates.TemplateResponse(
        "privacy.html", get_public_template_context(request=request, page="legal")
    )


@router.get("/aviso-legal", response_class=HTMLResponse)
async def legal_notice(request: Request):
    """Página pública de aviso legal."""
    return templates.TemplateResponse(
        "legal.html", get_public_template_context(request=request, page="legal")
    )
