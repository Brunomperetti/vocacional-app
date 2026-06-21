"""Servicio central para reconstruir resultados vocacionales desde datos de sesión."""

from app.data.questions import TEST_QUESTIONS
from app.services.participant_service import get_display_name
from app.services.profile_summary_service import build_result_insights
from app.services.recommendation_service import recommend_careers
from app.services.scoring_service import (
    build_profile_code,
    calculate_riasec_percentages,
    calculate_riasec_scores,
    get_top_dimensions,
)

EXPECTED_ANSWER_COUNT = len(TEST_QUESTIONS)
QUESTION_IDS = tuple(question["id"] for question in TEST_QUESTIONS)


def validate_complete_answers(answers: dict | None) -> None:
    """Valida que existan todas las respuestas requeridas y que sean valores Likert válidos."""
    if not isinstance(answers, dict):
        raise ValueError("No hay respuestas guardadas para reconstruir el resultado.")

    missing_question_ids = [question_id for question_id in QUESTION_IDS if question_id not in answers]
    if missing_question_ids or len(answers) < EXPECTED_ANSWER_COUNT:
        raise ValueError("Faltan respuestas para reconstruir el resultado.")

    for question_id in QUESTION_IDS:
        try:
            value = int(answers[question_id])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"La respuesta {question_id} debe ser un número entre 1 y 5.") from exc
        if value < 1 or value > 5:
            raise ValueError(f"La respuesta {question_id} debe estar entre 1 y 5.")


def build_result_from_session_data(participant: dict | None, answers: dict | None) -> dict:
    """Construye el resultado completo usando únicamente participante y respuestas de sesión."""
    validate_complete_answers(answers)
    participant_data = participant if isinstance(participant, dict) else {}

    scores = calculate_riasec_scores(answers)
    percentages = calculate_riasec_percentages(scores)
    top_dimensions = get_top_dimensions(percentages)
    profile_code = build_profile_code(top_dimensions)
    recommended_careers = recommend_careers(percentages)
    insights = build_result_insights(top_dimensions, profile_code, percentages, recommended_careers)
    display_name = get_display_name(participant_data)

    return {
        "participant": participant_data,
        "display_name": display_name,
        "percentages": percentages,
        "top_dimensions": top_dimensions,
        "profile_code": profile_code,
        "recommended_careers": recommended_careers,
        "insights": insights,
    }
