"""Helpers de configuración leídos desde variables de entorno."""

import os


def get_donation_url() -> str | None:
    """Devuelve la URL externa de aporte voluntario si está configurada."""
    donation_url = os.getenv("DONATION_URL", "").strip()
    return donation_url or None
