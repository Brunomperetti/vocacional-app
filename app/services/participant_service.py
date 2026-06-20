"""Helpers para normalizar y validar datos iniciales del participante."""

import re
from collections.abc import Mapping

PARTICIPANT_FIELDS = ("name", "email", "age", "current_status", "location")
CURRENT_STATUS_OPTIONS = (
    "Estoy en secundaria",
    "Terminé la secundaria",
    "Estoy estudiando una carrera",
    "Quiero cambiar de carrera",
    "Estoy trabajando y quiero reorientarme",
    "Otro",
)
_EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def clean_participant_data(form_data: Mapping[str, object]) -> dict[str, str]:
    """Devuelve los campos del participante como strings limpios."""
    participant = {}
    for field in PARTICIPANT_FIELDS:
        value = form_data.get(field, "")
        participant[field] = str(value).strip() if value is not None else ""
    return participant


def validate_participant_data(participant: dict[str, str]) -> list[str]:
    """Valida solo los campos opcionales que fueron completados."""
    errors = []

    email = participant.get("email", "")
    if email and not _EMAIL_PATTERN.match(email):
        errors.append("Ingresá un email válido o dejá el campo vacío.")

    age = participant.get("age", "")
    if age:
        try:
            numeric_age = int(age)
        except ValueError:
            errors.append("La edad debe ser un número entre 12 y 80, o podés dejarla vacía.")
        else:
            if numeric_age < 12 or numeric_age > 80:
                errors.append("La edad debe estar entre 12 y 80, o podés dejarla vacía.")

    current_status = participant.get("current_status", "")
    if current_status and current_status not in CURRENT_STATUS_OPTIONS:
        errors.append("Seleccioná una situación actual válida o dejá el campo vacío.")

    return errors


def get_display_name(participant: dict[str, str]) -> str:
    """Devuelve el nombre para mostrar o un fallback genérico."""
    name = participant.get("name", "").strip()
    return name or "Tu"
