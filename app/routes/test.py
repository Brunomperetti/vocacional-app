"""Rutas iniciales del test vocacional."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.data.questions import TEST_QUESTIONS, get_all_questions
from app.services.recommendation_service import recommend_careers
from app.services.scoring_service import (
    build_profile_code,
    calculate_riasec_percentages,
    calculate_riasec_scores,
    get_top_dimensions,
)

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/test", tags=["test"])

DIMENSIONS = {
    "R": "Realista",
    "I": "Investigativo",
    "A": "Artístico",
    "S": "Social",
    "E": "Emprendedor",
    "C": "Convencional",
}
LIKERT_OPTIONS = [
    (1, "No me interesa nada"),
    (2, "Me interesa poco"),
    (3, "Neutral"),
    (4, "Me interesa"),
    (5, "Me interesa mucho"),
]


def _build_test_context(request: Request, error: str | None = None) -> dict:
    """Construye el contexto compartido para renderizar el formulario del test."""
    grouped_questions = [
        {
            "code": code,
            "name": name,
            "questions": [
                question
                for question in get_all_questions()
                if question["dimension"] == code
            ],
        }
        for code, name in DIMENSIONS.items()
    ]
    return {
        "request": request,
        "grouped_questions": grouped_questions,
        "likert_options": LIKERT_OPTIONS,
        "error": error,
    }


@router.get("", response_class=HTMLResponse)
async def test_start(request: Request):
    """Pantalla inicial del test vocacional con preguntas RIASEC."""
    return templates.TemplateResponse("test_start.html", _build_test_context(request))


@router.post("", response_class=HTMLResponse)
async def process_test(request: Request):
    """Procesa respuestas RIASEC y muestra un resultado calculado."""
    form = await request.form()
    question_ids = [question["id"] for question in TEST_QUESTIONS]
    answers = {question_id: form.get(question_id) for question_id in question_ids}
    missing_answers = [question_id for question_id, value in answers.items() if value is None]

    if missing_answers:
        error = "Respondé todas las preguntas antes de ver tu resultado."
        return templates.TemplateResponse(
            "test_start.html",
            _build_test_context(request, error=error),
            status_code=400,
        )

    try:
        scores = calculate_riasec_scores(answers)
    except (KeyError, TypeError, ValueError):
        error = "Hay respuestas inválidas. Revisá el formulario y volvé a intentarlo."
        return templates.TemplateResponse(
            "test_start.html",
            _build_test_context(request, error=error),
            status_code=400,
        )

    percentages = calculate_riasec_percentages(scores)
    top_dimensions = get_top_dimensions(percentages)
    profile_code = build_profile_code(top_dimensions)
    recommendations = recommend_careers(percentages)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "scores": percentages,
            "top_dimensions": top_dimensions,
            "profile_code": profile_code,
            "recommendations": recommendations,
            "is_demo": False,
        },
    )
