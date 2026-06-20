"""Servicios de recomendación de carreras por compatibilidad RIASEC."""

from app.data.careers import CAREERS, RIASEC_DIMENSIONS

MAX_CAREER_PROFILE_VALUE = 5


def calculate_career_match(user_percentages: dict, career_profile: dict) -> int:
    """Calcula compatibilidad RIASEC entre el usuario y una carrera, de 0 a 100."""
    similarities = []
    for dimension in RIASEC_DIMENSIONS:
        user_value = max(0, min(100, int(user_percentages.get(dimension, 0))))
        career_value = max(
            0,
            min(
                100,
                round((int(career_profile.get(dimension, 1)) / MAX_CAREER_PROFILE_VALUE) * 100),
            ),
        )
        similarities.append(100 - abs(user_value - career_value))

    return max(0, min(100, round(sum(similarities) / len(similarities))))


def recommend_careers(user_percentages: dict, limit: int = 8) -> list[dict[str, object]]:
    """Devuelve carreras ordenadas por compatibilidad RIASEC descendente."""
    recommendations = []
    for career in CAREERS:
        match_percentage = calculate_career_match(
            user_percentages,
            career["riasec_profile"],
        )
        recommendations.append(
            {
                "name": career["name"],
                "description": career["description"],
                "area": career["area"],
                "study_type": career["study_type"],
                "duration": career["duration"],
                "skills": career["skills"],
                "match_percentage": match_percentage,
            }
        )

    return sorted(
        recommendations,
        key=lambda item: item["match_percentage"],
        reverse=True,
    )[:limit]


def get_demo_recommendations() -> list[dict[str, object]]:
    """Devuelve recomendaciones de ejemplo basadas en un perfil demo."""
    demo_scores = {"R": 62, "I": 88, "A": 54, "S": 76, "E": 61, "C": 48}
    return recommend_careers(demo_scores, limit=8)
