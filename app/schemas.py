"""Esquemas Pydantic iniciales."""

from pydantic import BaseModel, ConfigDict


class CareerRead(BaseModel):
    """Representación pública de una carrera."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    riasec_profile: str
