"""Utilidades de autenticación para el panel administrador."""

import os
import secrets

from fastapi import Request

ADMIN_SESSION_KEY = "admin_authenticated"


def get_admin_credentials() -> tuple[str | None, str | None]:
    """Obtiene las credenciales admin desde variables de entorno."""
    return os.getenv("ADMIN_USERNAME"), os.getenv("ADMIN_PASSWORD")


def is_admin_configured() -> bool:
    """Indica si las credenciales admin están configuradas."""
    username, password = get_admin_credentials()
    return bool(username and password)


def verify_admin_credentials(username: str, password: str) -> bool:
    """Valida credenciales admin usando comparación segura."""
    admin_username, admin_password = get_admin_credentials()
    if not admin_username or not admin_password:
        return False

    username_matches = secrets.compare_digest(username, admin_username)
    password_matches = secrets.compare_digest(password, admin_password)
    return username_matches and password_matches


def login_admin(request: Request) -> None:
    """Marca la sesión actual como autenticada para administración."""
    request.session[ADMIN_SESSION_KEY] = True


def logout_admin(request: Request) -> None:
    """Elimina la autenticación admin de la sesión actual."""
    request.session.pop(ADMIN_SESSION_KEY, None)


def is_admin_authenticated(request: Request) -> bool:
    """Indica si la sesión actual está autenticada como admin."""
    return request.session.get(ADMIN_SESSION_KEY) is True
