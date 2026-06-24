"""Rutas públicas generales."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from app.database import get_db
from app.services.settings_service import get_app_name, get_public_template_context
from app.services.testimonial_service import get_approved_testimonials

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["get_app_name"] = get_app_name
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """Landing principal de Vocación360."""
    testimonials = []
    try:
        testimonials = get_approved_testimonials(db, limit=6)
    except Exception:
        testimonials = []
    return templates.TemplateResponse(
        "index.html",
        get_public_template_context(
            request=request, page="landing", testimonials=testimonials
        ),
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
