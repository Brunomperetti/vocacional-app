"""Rutas administrativas temporales."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.auth import is_admin_placeholder
from app.database import get_db
from app.models import TestResult

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard administrativo básico sin login real."""
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
            "has_access": is_admin_placeholder(),
            "total_results": total_results,
            "latest_results": latest_results,
            "db_error": db_error,
        },
    )
