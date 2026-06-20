"""Servicios iniciales de scoring RIASEC."""


def get_demo_riasec_scores() -> dict[str, int]:
    """Devuelve un scoring de demostración para la pantalla de resultado."""
    return {
        "Realista": 62,
        "Investigador": 88,
        "Artístico": 54,
        "Social": 76,
        "Emprendedor": 61,
        "Convencional": 48,
    }
