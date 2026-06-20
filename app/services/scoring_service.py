"""Servicios de scoring RIASEC."""

from app.data.questions import TEST_QUESTIONS

DIMENSION_LABELS: dict[str, str] = {
    "R": "Realista",
    "I": "Investigativo",
    "A": "Artístico",
    "S": "Social",
    "E": "Emprendedor",
    "C": "Convencional",
}

DIMENSION_DESCRIPTIONS: dict[str, str] = {
    "R": "Preferencia por actividades prácticas, técnicas, manuales o vinculadas al mundo físico.",
    "I": "Interés por analizar, investigar, resolver problemas y comprender cómo funcionan las cosas.",
    "A": "Interés por crear, expresar ideas, imaginar y trabajar con contenido visual, escrito o creativo.",
    "S": "Interés por ayudar, enseñar, acompañar, comunicar y trabajar con personas.",
    "E": "Interés por liderar, persuadir, vender, iniciar proyectos y tomar decisiones.",
    "C": "Interés por organizar, administrar, ordenar información, procesos o datos.",
}

DIMENSION_RECOMMENDATIONS: dict[str, list[str]] = {
    "I": ["Ciencia de Datos", "Ingeniería", "Medicina", "Biotecnología", "Investigación"],
    "S": ["Psicología", "Educación", "Trabajo Social", "Recursos Humanos", "Enfermería"],
    "A": ["Diseño UX/UI", "Comunicación", "Diseño Gráfico", "Producción Audiovisual", "Publicidad"],
    "E": ["Marketing", "Administración", "Negocios Digitales", "Comercio", "Emprendimiento"],
    "C": ["Contabilidad", "Administración", "Analítica de Datos", "Gestión", "Finanzas"],
    "R": ["Ingeniería", "Arquitectura", "Mecánica", "Agronomía", "Oficios Técnicos"],
}

QUESTION_DIMENSIONS = {question["id"]: question["dimension"] for question in TEST_QUESTIONS}
MAX_SCORE_BY_DIMENSION = 30


def calculate_riasec_scores(answers: dict) -> dict[str, int]:
    """Calcula el puntaje RIASEC sumando respuestas de 1 a 5 por dimensión."""
    scores = {code: 0 for code in DIMENSION_LABELS}

    for question_id, dimension in QUESTION_DIMENSIONS.items():
        value = int(answers[question_id])
        if value < 1 or value > 5:
            raise ValueError(f"La respuesta {question_id} debe estar entre 1 y 5.")
        scores[dimension] += value

    return scores


def calculate_riasec_percentages(scores: dict) -> dict[str, int]:
    """Convierte puntajes RIASEC a porcentajes enteros sobre 30 puntos."""
    return {
        dimension: round((int(score) / MAX_SCORE_BY_DIMENSION) * 100)
        for dimension, score in scores.items()
    }


def get_top_dimensions(percentages: dict, limit: int = 3) -> list[dict[str, object]]:
    """Devuelve las dimensiones principales ordenadas de mayor a menor porcentaje."""
    sorted_dimensions = sorted(
        percentages.items(),
        key=lambda item: item[1],
        reverse=True,
    )
    return [
        {
            "code": code,
            "name": DIMENSION_LABELS[code],
            "percentage": percentage,
            "description": DIMENSION_DESCRIPTIONS[code],
        }
        for code, percentage in sorted_dimensions[:limit]
    ]


def build_profile_code(top_dimensions: list) -> str:
    """Arma el código vocacional con las letras de las dimensiones principales."""
    return "".join(dimension["code"] for dimension in top_dimensions)


def get_recommendations_for_dimension(dimension_code: str) -> list[dict[str, str]]:
    """Devuelve recomendaciones temporales de carreras según la dimensión principal."""
    dimension_name = DIMENSION_LABELS[dimension_code]
    return [
        {
            "career": career,
            "reason": f"Se relaciona con tu perfil {dimension_name.lower()} predominante.",
        }
        for career in DIMENSION_RECOMMENDATIONS[dimension_code]
    ]


def get_demo_riasec_scores() -> dict[str, int]:
    """Devuelve un scoring de demostración para la pantalla de resultado."""
    return {
        "R": 62,
        "I": 88,
        "A": 54,
        "S": 76,
        "E": 61,
        "C": 48,
    }
