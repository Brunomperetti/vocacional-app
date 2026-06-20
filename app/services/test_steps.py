"""Helpers for the RIASEC test wizard steps."""

from app.data.questions import get_questions_by_dimension
from app.services.scoring_service import DIMENSION_DESCRIPTIONS, DIMENSION_LABELS

STEP_DIMENSIONS: dict[int, str] = {
    1: "R",
    2: "I",
    3: "A",
    4: "S",
    5: "E",
    6: "C",
}
TOTAL_STEPS = len(STEP_DIMENSIONS)


def get_step_questions(step: int) -> list[dict[str, str]]:
    """Devuelve las 6 preguntas asociadas a un paso del wizard."""
    dimension = STEP_DIMENSIONS[step]
    return get_questions_by_dimension(dimension)


def get_step_dimension_label(step: int) -> str:
    """Devuelve el nombre de la dimensión asociada a un paso."""
    return DIMENSION_LABELS[STEP_DIMENSIONS[step]]


def get_step_dimension_description(step: int) -> str:
    """Devuelve la descripción breve de la dimensión asociada a un paso."""
    return DIMENSION_DESCRIPTIONS[STEP_DIMENSIONS[step]]
