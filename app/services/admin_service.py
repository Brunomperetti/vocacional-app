"""Helpers para vistas y exportaciones del panel administrador."""

from __future__ import annotations

import json
from typing import Any


def safe_json_loads(value: str | None, fallback: Any) -> Any:
    """Parsea JSON de forma segura y devuelve fallback ante valores vacíos o inválidos."""
    if not value:
        return fallback

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return fallback
