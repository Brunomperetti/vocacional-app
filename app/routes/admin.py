"""Rutas administrativas temporales."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth import is_admin_placeholder

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Dashboard administrativo básico sin login real."""
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "has_access": is_admin_placeholder()},
    )
