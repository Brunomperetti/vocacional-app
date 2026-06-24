"""Tests for testimonial moderation helpers."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Testimonial
from app.services.testimonial_service import (
    create_testimonial,
    get_approved_testimonials,
    validate_testimonial_data,
)


def _session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_validate_empty_comment_returns_error():
    errors = validate_testimonial_data({"comment": "", "public_consent": True})

    assert any("obligatorio" in error for error in errors)


def test_validate_short_comment_returns_error():
    errors = validate_testimonial_data({"comment": "corto", "public_consent": True})

    assert any("al menos 10" in error for error in errors)


def test_create_testimonial_defaults_to_not_approved():
    db = _session()

    testimonial = create_testimonial(
        db, {"name": "Ana", "comment": "Me ayudó mucho el resultado.", "public_consent": True}
    )

    assert testimonial.approved is False


def test_get_approved_testimonials_only_returns_approved():
    db = _session()
    db.add_all([
        Testimonial(comment="Pendiente de revisión", approved=False),
        Testimonial(comment="Comentario aprobado", approved=True),
    ])
    db.commit()

    testimonials = get_approved_testimonials(db)

    assert len(testimonials) == 1
    assert testimonials[0].comment == "Comentario aprobado"
