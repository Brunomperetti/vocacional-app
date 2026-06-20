"""Servicios iniciales de recomendación de carreras."""


def get_demo_recommendations() -> list[dict[str, str]]:
    """Devuelve recomendaciones de ejemplo basadas en un perfil demo."""
    return [
        {
            "career": "Psicología",
            "reason": "Combina interés social, análisis de conducta y acompañamiento humano.",
        },
        {
            "career": "Ingeniería en Software",
            "reason": "Aprovecha habilidades investigadoras para resolver problemas con tecnología.",
        },
        {
            "career": "Diseño UX/UI",
            "reason": "Integra creatividad, investigación de usuarios y mejora de experiencias digitales.",
        },
    ]
