"""Rutas administrativas protegidas por login simple."""

import csv
import io

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, selectinload

from app.auth import (
    is_admin_authenticated,
    is_admin_configured,
    login_admin,
    logout_admin,
    verify_admin_credentials,
)
from app.database import get_db
from app.models import TestResult
from app.services.admin_service import safe_json_loads
from app.services.settings_service import get_app_name

ADMIN_CONFIG_MESSAGE = (
    "El acceso admin todavía no está configurado. Definí ADMIN_USERNAME y "
    "ADMIN_PASSWORD en variables de entorno."
)
RIASEC_CODES = ("R", "I", "A", "S", "E", "C")

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["get_app_name"] = get_app_name
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


def _admin_login_redirect() -> RedirectResponse:
    """Redirige al login admin cuando no hay sesión autenticada."""
    return RedirectResponse(url="/admin/login", status_code=303)


def _join_names(items: list[dict], key: str = "name") -> str:
    """Une nombres o códigos para columnas compactas de CSV."""
    values = [str(item.get(key) or item.get("code") or "").strip() for item in items]
    return ", ".join(value for value in values if value)


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
    """Dashboard administrativo protegido por sesión."""
    if not is_admin_authenticated(request):
        return _admin_login_redirect()

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


@router.get("/results/{result_id}", response_class=HTMLResponse)
async def admin_result_detail(
    result_id: int, request: Request, db: Session = Depends(get_db)
):
    """Muestra el detalle completo de un resultado guardado."""
    if not is_admin_authenticated(request):
        return _admin_login_redirect()

    result = (
        db.query(TestResult)
        .options(selectinload(TestResult.answers))
        .filter(TestResult.id == result_id)
        .first()
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Resultado no encontrado")

    return templates.TemplateResponse(
        "admin/result_detail.html",
        {
            "request": request,
            "result": result,
            "percentages": safe_json_loads(result.percentages_json, {}),
            "top_dimensions": safe_json_loads(result.top_dimensions_json, []),
            "recommended_careers": safe_json_loads(result.recommended_careers_json, []),
            "insights": safe_json_loads(result.insights_json, {}),
            "riasec_codes": RIASEC_CODES,
            "answers": sorted(result.answers, key=lambda answer: answer.question_id),
        },
    )


@router.get("/export.csv")
async def admin_export_csv(request: Request, db: Session = Depends(get_db)):
    """Exporta todos los resultados guardados en formato CSV."""
    if not is_admin_authenticated(request):
        return _admin_login_redirect()

    output = io.StringIO()
    fieldnames = [
        "id", "created_at", "name", "whatsapp", "age", "current_status", "location",
        "consent_accepted", "profile_code", *RIASEC_CODES, "top_dimensions", "top_careers",
        "user_agent", "ip_address",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    results = db.query(TestResult).order_by(desc(TestResult.created_at)).all()
    for result in results:
        percentages = safe_json_loads(result.percentages_json, {})
        top_dimensions = safe_json_loads(result.top_dimensions_json, [])
        recommended_careers = safe_json_loads(result.recommended_careers_json, [])
        row = {
            "id": result.id,
            "created_at": result.created_at.isoformat() if result.created_at else "",
            "name": result.name or "",
            "whatsapp": result.whatsapp or "",
            "age": result.age or "",
            "current_status": result.current_status or "",
            "location": result.location or "",
            "consent_accepted": result.consent_accepted,
            "profile_code": result.profile_code,
            "top_dimensions": _join_names(top_dimensions),
            "top_careers": _join_names(recommended_careers[:3]),
            "user_agent": result.user_agent or "",
            "ip_address": result.ip_address or "",
        }
        for code in RIASEC_CODES:
            row[code] = percentages.get(code, "")
        writer.writerow(row)

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="resultados-vocacionales.csv"'},
    )
