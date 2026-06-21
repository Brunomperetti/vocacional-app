"""Rutas administrativas protegidas por login simple."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.auth import (
    is_admin_authenticated,
    is_admin_configured,
    login_admin,
    logout_admin,
    verify_admin_credentials,
)
from app.database import get_db
from app.models import TestResult

ADMIN_CONFIG_MESSAGE = (
    "El acceso admin todavía no está configurado. Definí ADMIN_USERNAME y "
    "ADMIN_PASSWORD en variables de entorno."
)

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/admin", tags=["admin"])


def _login_response(
    request: Request, error: str | None = None, status_code: int = 200
) -> HTMLResponse:
    """Renderiza el formulario de acceso admin."""
    config_message = None if is_admin_configured() else ADMIN_CONFIG_MESSAGE
    return templates.TemplateResponse(
        "admin/login.html",
        {
            "request": request,
            "error": error,
            "config_message": config_message,
        },
        status_code=status_code,
    )


@router.get("/login", response_class=HTMLResponse)
async def admin_login_form(request: Request):
    """Muestra el formulario de login admin."""
    if is_admin_authenticated(request):
        return RedirectResponse(url="/admin", status_code=303)
    return _login_response(request)


@router.post("/login", response_class=HTMLResponse)
async def admin_login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Valida credenciales admin y crea la sesión si son correctas."""
    if verify_admin_credentials(username, password):
        login_admin(request)
        return RedirectResponse(url="/admin", status_code=303)

    return _login_response(
        request, error="Usuario o contraseña incorrectos.", status_code=401
    )


@router.get("/logout")
async def admin_logout(request: Request):
    """Cierra la sesión admin y vuelve al login."""
    logout_admin(request)
    return RedirectResponse(url="/admin/login", status_code=303)


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard administrativo básico protegido por sesión."""
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=303)

    total_results = 0
    latest_results = []
    db_error = None
    try:
        total_results = db.query(func.count(TestResult.id)).scalar() or 0
        latest_results = (
            db.query(TestResult)
            .order_by(desc(TestResult.created_at))
            .limit(10)
            .all()
        )
    except Exception:
        db_error = "No se pudieron cargar los resultados guardados."

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "total_results": total_results,
            "latest_results": latest_results,
            "db_error": db_error,
        },
    )
