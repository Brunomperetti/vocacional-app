"""Modelos iniciales de datos."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Career(Base):
    """Carrera sugerible por el sistema vocacional."""

    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    riasec_profile: Mapped[str] = mapped_column(String(6), nullable=False, default="RIASEC")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TestResult(Base):
    """Resultado completo persistido de un test vocacional finalizado."""

    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(30), nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_status: Mapped[str | None] = mapped_column(String(120), nullable=True)
    location: Mapped[str | None] = mapped_column(String(180), nullable=True)
    consent_accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    profile_code: Mapped[str] = mapped_column(String(6), nullable=False)
    percentages_json: Mapped[str] = mapped_column(Text, nullable=False)
    top_dimensions_json: Mapped[str] = mapped_column(Text, nullable=False)
    recommended_careers_json: Mapped[str] = mapped_column(Text, nullable=False)
    insights_json: Mapped[str] = mapped_column(Text, nullable=False)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)

    answers: Mapped[list["TestAnswer"]] = relationship(
        back_populates="test_result",
        cascade="all, delete-orphan",
    )
    testimonials: Mapped[list["Testimonial"]] = relationship(back_populates="source_result")


class TestAnswer(Base):
    """Respuesta individual asociada a un resultado persistido."""

    __tablename__ = "test_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    test_result_id: Mapped[int] = mapped_column(ForeignKey("test_results.id"), nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(String(10), nullable=False)
    dimension: Mapped[str] = mapped_column(String(1), nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)

    test_result: Mapped[TestResult] = relationship(back_populates="answers")


class Testimonial(Base):
    """Comentario de usuario pendiente o aprobado para mostrar en la landing."""

    __tablename__ = "testimonials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    source_result_id: Mapped[int | None] = mapped_column(ForeignKey("test_results.id"), nullable=True, index=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)

    source_result: Mapped[TestResult | None] = relationship(back_populates="testimonials")
