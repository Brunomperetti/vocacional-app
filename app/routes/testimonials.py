"""Rutas públicas para comentarios/testimonios."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
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


def sanitize_return_to(return_to: str | None) -> str:
    """Devuelve una ruta interna segura para redirigir después del comentario."""
    if not return_to:
        return "/"
    cleaned = return_to.strip()
    parsed = urlsplit(cleaned)
    if (
        not cleaned.startswith("/")
        or cleaned.startswith("//")
        or parsed.scheme in {"http", "https"}
        or parsed.netloc
    ):
        return "/"
    return cleaned


def add_comment_status(return_to: str, status: str) -> str:
    """Agrega el estado del comentario a una URL interna conservando su query."""
    safe_return_to = sanitize_return_to(return_to)
    parsed = urlsplit(safe_return_to)
    query_params = parse_qsl(parsed.query, keep_blank_values=True)
    query_params = [(key, value) for key, value in query_params if key != "comentario"]
    query_params.append(("comentario", status))
    return urlunsplit(("", "", parsed.path or "/", urlencode(query_params), parsed.fragment))


@router.post("/testimonios")
async def submit_testimonial(
    request: Request,
    name: str = Form(""),
    comment: str = Form(""),
    public_consent: str | None = Form(None),
    return_to: str = Form("/"),
    db: Session = Depends(get_db),
):
    """Guarda un comentario pendiente de aprobación admin."""
    safe_return_to = sanitize_return_to(return_to)
    data = clean_testimonial_data(
        {"name": name, "comment": comment, "public_consent": public_consent}
    )
    errors = validate_testimonial_data(data)
    if errors:
        return RedirectResponse(url=add_comment_status(safe_return_to, "error"), status_code=303)

    source_result_id = request.session.get("last_result_id")
    create_testimonial(db, data, request=request, source_result_id=source_result_id)
    return RedirectResponse(url=add_comment_status(safe_return_to, "enviado"), status_code=303)


@router.get("/testimonios/gracias", response_class=HTMLResponse)
async def testimonial_thanks(request: Request):
    """Página de confirmación para comentarios enviados."""
    return templates.TemplateResponse(
        "testimonial_thanks.html",
        get_public_template_context(request=request, page="thanks"),
    )
