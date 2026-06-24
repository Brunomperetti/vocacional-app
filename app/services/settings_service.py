"""Helpers de configuración leídos desde variables de entorno."""

import os


def get_donation_url() -> str | None:
    """Devuelve la URL externa de aporte voluntario si está configurada."""
    donation_url = os.getenv("DONATION_URL", "").strip()
    return donation_url or None


def get_public_app_url() -> str | None:
    """Devuelve la URL pública de la app si está configurada."""
    public_app_url = os.getenv("PUBLIC_APP_URL", "").strip().rstrip("/")
    return public_app_url or None


def get_creator_linkedin_url() -> str | None:
    """Devuelve el link HTTPS del perfil del creador si está configurado."""
    creator_linkedin_url = os.getenv("CREATOR_LINKEDIN_URL", "").strip()
    if not creator_linkedin_url.startswith("https://"):
        return None
    return creator_linkedin_url


def get_app_name() -> str:
    """Devuelve el nombre público configurable de la aplicación."""
    return os.getenv("APP_NAME", "").strip() or "Vocación360"


def get_ga_measurement_id() -> str | None:
    """Devuelve el Measurement ID de GA4 si está configurado."""
    ga_measurement_id = os.getenv("GA_MEASUREMENT_ID", "").strip()
    return ga_measurement_id or None


def get_meta_pixel_id() -> str | None:
    """Devuelve el Pixel ID de Meta si está configurado."""
    meta_pixel_id = os.getenv("META_PIXEL_ID", "").strip()
    return meta_pixel_id or None


def get_public_template_context(**extra) -> dict:
    """Construye contexto común para templates públicos."""
    context = {
        "donation_url": get_donation_url(),
        "ga_measurement_id": get_ga_measurement_id(),
        "meta_pixel_id": get_meta_pixel_id(),
        "creator_linkedin_url": get_creator_linkedin_url(),
    }
    context.update(extra)
    return context
