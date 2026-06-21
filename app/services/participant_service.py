"""Helpers para normalizar y validar datos iniciales del participante."""

import re
from collections.abc import Mapping

PARTICIPANT_FIELDS = ("name", "whatsapp", "age", "current_status", "location")
CONSENT_ERROR = "Para comenzar, necesitás aceptar el consentimiento de uso de datos."
CURRENT_STATUS_OPTIONS = (
    "Estoy en secundaria",
    "Terminé la secundaria",
    "Estoy estudiando una carrera",
    "Quiero cambiar de carrera",
    "Estoy trabajando y quiero reorientarme",
    "Otro",
)
_WHATSAPP_ALLOWED_PATTERN = re.compile(r"^\+?[\d\s()\-]+$")


def normalize_whatsapp(value: str) -> str:
    """Normaliza WhatsApp conservando solo números y un signo + inicial si existe."""
    raw_value = str(value or "").strip()
    if not raw_value:
        return ""

    digits = "".join(character for character in raw_value if character.isdigit())
    prefix = "+" if raw_value.startswith("+") else ""
    return f"{prefix}{digits}"


def clean_participant_data(form_data: Mapping[str, object]) -> dict[str, str | bool]:
    """Devuelve los campos del participante como strings limpios y normalizados."""
    participant = {}
    for field in PARTICIPANT_FIELDS:
        value = form_data.get(field, "")
        participant[field] = str(value).strip() if value is not None else ""

    whatsapp = participant.get("whatsapp", "")
    if whatsapp and _WHATSAPP_ALLOWED_PATTERN.match(whatsapp):
        participant["whatsapp"] = normalize_whatsapp(whatsapp)

    consent_value = form_data.get("consent_accepted")
    participant["consent_accepted"] = str(consent_value).lower() in {"1", "true", "on", "yes", "accepted"}
    return participant


def validate_participant_data(participant: dict[str, str | bool]) -> list[str]:
    """Valida solo los campos opcionales que fueron completados."""
    errors = []

    if not participant.get("consent_accepted"):
        errors.append(CONSENT_ERROR)

    whatsapp = participant.get("whatsapp", "")
    if whatsapp:
        whatsapp_digits = whatsapp[1:] if whatsapp.startswith("+") else whatsapp
        if (
            not _WHATSAPP_ALLOWED_PATTERN.match(whatsapp)
            or not whatsapp_digits.isdigit()
            or len(whatsapp_digits) < 6
            or len(whatsapp_digits) > 15
        ):
            errors.append("Ingresá un WhatsApp válido o dejá el campo vacío.")

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
