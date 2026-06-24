"""Rutas públicas para comentarios/testimonios."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.settings_service import get_app_name, get_public_template_context
from app.services.testimonial_service import (
    clean_testimonial_data,
    create_testimonial,
    validate_testimonial_data,
)

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["get_app_name"] = get_app_name
router = APIRouter(tags=["testimonials"])


@router.post("/testimonios")
async def submit_testimonial(
    request: Request,
    name: str = Form(""),
    comment: str = Form(""),
    public_consent: str | None = Form(None),
    db: Session = Depends(get_db),
):
    """Guarda un comentario pendiente de aprobación admin."""
    data = clean_testimonial_data(
        {"name": name, "comment": comment, "public_consent": public_consent}
    )
    errors = validate_testimonial_data(data)
    if errors:
        return templates.TemplateResponse(
            "testimonial_error.html",
            get_public_template_context(request=request, page="result", errors=errors),
            status_code=400,
        )

    source_result_id = request.session.get("last_result_id")
    create_testimonial(db, data, request=request, source_result_id=source_result_id)
    return RedirectResponse(url="/testimonios/gracias", status_code=303)


@router.get("/testimonios/gracias", response_class=HTMLResponse)
async def testimonial_thanks(request: Request):
    """Página de confirmación para comentarios enviados."""
    return templates.TemplateResponse(
        "testimonial_thanks.html",
        get_public_template_context(request=request, page="thanks"),
    )
