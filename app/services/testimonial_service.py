"""Servicios para comentarios/testimonios públicos con aprobación admin."""

from __future__ import annotations

from sqlalchemy import desc
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.models import Testimonial

MAX_NAME_LENGTH = 80
MAX_COMMENT_LENGTH = 500
MIN_COMMENT_LENGTH = 10


def clean_testimonial_data(data: dict) -> dict:
    """Normaliza campos ingresados por usuarios antes de validar o persistir."""
    return {
        "name": str(data.get("name") or "").strip()[:MAX_NAME_LENGTH] or None,
        "comment": str(data.get("comment") or "").strip(),
        "public_consent": data.get("public_consent") in (True, "on", "true", "1", "yes"),
    }


def validate_testimonial_data(data: dict) -> list[str]:
    """Valida reglas mínimas para comentarios publicables bajo revisión."""
    errors: list[str] = []
    comment = str(data.get("comment") or "").strip()
    name = str(data.get("name") or "").strip()

    if not comment:
        errors.append("El comentario es obligatorio.")
    elif len(comment) < MIN_COMMENT_LENGTH:
        errors.append("El comentario debe tener al menos 10 caracteres.")
    elif len(comment) > MAX_COMMENT_LENGTH:
        errors.append("El comentario no puede superar los 500 caracteres.")

    if len(name) > MAX_NAME_LENGTH:
        errors.append("El nombre no puede superar los 80 caracteres.")

    if not data.get("public_consent"):
        errors.append("Necesitás aceptar que el comentario pueda mostrarse públicamente.")

    return errors


def create_testimonial(
    db: Session,
    data: dict,
    request: Request | None = None,
    source_result_id: int | None = None,
) -> Testimonial:
    """Crea un comentario pendiente de aprobación."""
    cleaned = clean_testimonial_data(data)
    testimonial = Testimonial(
        name=cleaned["name"],
        comment=cleaned["comment"],
        approved=False,
        source_result_id=source_result_id,
        ip_address=request.client.host if request and request.client else None,
        user_agent=request.headers.get("user-agent")[:255] if request else None,
    )
    db.add(testimonial)
    db.commit()
    db.refresh(testimonial)
    return testimonial


def get_approved_testimonials(db: Session, limit: int = 6) -> list[Testimonial]:
    """Devuelve comentarios aprobados recientes para la landing pública."""
    return (
        db.query(Testimonial)
        .filter(Testimonial.approved.is_(True))
        .order_by(desc(Testimonial.created_at))
        .limit(limit)
        .all()
    )


def get_pending_testimonials(db: Session, limit: int = 50) -> list[Testimonial]:
    """Devuelve comentarios pendientes para revisión administrativa."""
    return (
        db.query(Testimonial)
        .filter(Testimonial.approved.is_(False))
        .order_by(desc(Testimonial.created_at))
        .limit(limit)
        .all()
    )


def approve_testimonial(db: Session, testimonial_id: int) -> bool:
    """Marca un comentario como aprobado."""
    testimonial = db.get(Testimonial, testimonial_id)
    if testimonial is None:
        return False
    testimonial.approved = True
    db.commit()
    return True


def reject_or_delete_testimonial(db: Session, testimonial_id: int) -> bool:
    """Elimina un comentario rechazado o ya aprobado."""
    testimonial = db.get(Testimonial, testimonial_id)
    if testimonial is None:
        return False
    db.delete(testimonial)
    db.commit()
    return True
