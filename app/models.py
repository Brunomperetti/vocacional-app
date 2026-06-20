"""Modelos iniciales de datos."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Career(Base):
    """Carrera sugerible por el sistema vocacional."""

    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    riasec_profile: Mapped[str] = mapped_column(String(6), nullable=False, default="RIASEC")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
