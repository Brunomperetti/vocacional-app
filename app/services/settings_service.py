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


def get_app_name() -> str:
    """Devuelve el nombre público configurable de la aplicación."""
    return os.getenv("APP_NAME", "").strip() or "Vocación360"
