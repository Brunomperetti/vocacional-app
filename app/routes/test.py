"""Rutas del test vocacional RIASEC por etapas."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.data.questions import TEST_QUESTIONS
from app.services.participant_service import (
    CURRENT_STATUS_OPTIONS,
    clean_participant_data,
    get_display_name,
    validate_participant_data,
)
from app.services.profile_summary_service import build_result_insights
from app.services.recommendation_service import recommend_careers
from app.services.scoring_service import (
    DIMENSION_LABELS,
    build_profile_code,
    calculate_riasec_percentages,
    calculate_riasec_scores,
    get_top_dimensions,
)
from app.services.test_steps import (
    STEP_DIMENSIONS,
    TOTAL_STEPS,
    get_step_dimension_description,
    get_step_questions,
)

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/test", tags=["test"])

SESSION_ANSWERS_KEY = "answers"
SESSION_PARTICIPANT_KEY = "participant"
LIKERT_OPTIONS = [
    (1, "No me interesa nada"),
    (2, "Me interesa poco"),
    (3, "Neutral"),
    (4, "Me interesa"),
    (5, "Me interesa mucho"),
]


def _render_result(request: Request, answers: dict[str, str]) -> HTMLResponse:
    """Calcula y renderiza el resultado RIASEC final."""
    scores = calculate_riasec_scores(answers)
    percentages = calculate_riasec_percentages(scores)
    top_dimensions = get_top_dimensions(percentages)
    profile_code = build_profile_code(top_dimensions)
    recommendations = recommend_careers(percentages)
    insights = build_result_insights(top_dimensions, profile_code, percentages, recommendations)
    participant = request.session.get(SESSION_PARTICIPANT_KEY, {})
    display_name = get_display_name(participant)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "scores": percentages,
            "top_dimensions": top_dimensions,
            "profile_code": profile_code,
            "recommendations": recommendations,
            "insights": insights,
            "is_demo": False,
            "participant": participant,
            "display_name": display_name,
        },
    )


def _build_step_context(
    request: Request,
    step: int,
    error: str | None = None,
    submitted_answers: dict[str, str] | None = None,
) -> dict:
    """Construye el contexto compartido para un paso del test."""
    dimension = STEP_DIMENSIONS[step]
    progress_percentage = round((step / TOTAL_STEPS) * 100)
    session_answers = request.session.get(SESSION_ANSWERS_KEY, {})
    answers = {**session_answers, **(submitted_answers or {})}

    return {
        "request": request,
        "step": step,
        "total_steps": TOTAL_STEPS,
        "progress_percentage": progress_percentage,
        "dimension_code": dimension,
        "dimension_name": DIMENSION_LABELS[dimension],
        "dimension_description": get_step_dimension_description(step),
        "questions": get_step_questions(step),
        "likert_options": LIKERT_OPTIONS,
        "error": error,
        "answers": answers,
        "previous_step": step - 1 if step > 1 else None,
        "next_label": "Ver mi resultado" if step == TOTAL_STEPS else "Siguiente",
    }


@router.get("", response_class=HTMLResponse)
async def test_start(request: Request):
    """Pantalla inicial del test vocacional por etapas."""
    request.session.pop(SESSION_ANSWERS_KEY, None)
    return templates.TemplateResponse(
        "test_start.html",
        {
            "request": request,
            "total_steps": TOTAL_STEPS,
            "dimension_labels": DIMENSION_LABELS,
            "step_dimensions": STEP_DIMENSIONS,
            "current_status_options": CURRENT_STATUS_OPTIONS,
            "participant": request.session.get(SESSION_PARTICIPANT_KEY, {}),
            "errors": [],
        },
    )


@router.post("/iniciar", response_class=HTMLResponse)
async def start_test(request: Request):
    """Guarda datos iniciales opcionales y comienza el wizard."""
    form = await request.form()
    participant = clean_participant_data(form)
    errors = validate_participant_data(participant)

    if errors:
        return templates.TemplateResponse(
            "test_start.html",
            {
                "request": request,
                "total_steps": TOTAL_STEPS,
                "dimension_labels": DIMENSION_LABELS,
                "step_dimensions": STEP_DIMENSIONS,
                "current_status_options": CURRENT_STATUS_OPTIONS,
                "participant": participant,
                "errors": errors,
            },
            status_code=400,
        )

    request.session[SESSION_PARTICIPANT_KEY] = participant
    request.session[SESSION_ANSWERS_KEY] = {}
    return RedirectResponse(url="/test/paso/1", status_code=303)


@router.get("/paso/{step}", response_class=HTMLResponse)
async def show_test_step(request: Request, step: int):
    """Muestra las preguntas de una dimensión RIASEC en el wizard."""
    if step not in STEP_DIMENSIONS:
        return RedirectResponse(url="/test", status_code=303)

    return templates.TemplateResponse("test_step.html", _build_step_context(request, step))


@router.post("/paso/{step}", response_class=HTMLResponse)
async def process_test_step(request: Request, step: int):
    """Procesa un paso del test y avanza hasta calcular el resultado final."""
    if step not in STEP_DIMENSIONS:
        return RedirectResponse(url="/test", status_code=303)

    form = await request.form()
    questions = get_step_questions(step)
    question_ids = [question["id"] for question in questions]
    step_answers = {question_id: form.get(question_id) for question_id in question_ids}
    missing_answers = [question_id for question_id, value in step_answers.items() if value is None]

    if missing_answers:
        return templates.TemplateResponse(
            "test_step.html",
            _build_step_context(
                request,
                step,
                error="Respondé las 6 preguntas de esta etapa antes de continuar.",
                submitted_answers={key: value for key, value in step_answers.items() if value is not None},
            ),
            status_code=400,
        )

    try:
        normalized_answers = {
            question_id: str(int(value))
            for question_id, value in step_answers.items()
            if value is not None
        }
        if any(int(value) < 1 or int(value) > 5 for value in normalized_answers.values()):
            raise ValueError
    except (TypeError, ValueError):
        return templates.TemplateResponse(
            "test_step.html",
            _build_step_context(
                request,
                step,
                error="Hay respuestas inválidas. Revisá la etapa y volvé a intentarlo.",
            ),
            status_code=400,
        )

    accumulated_answers = request.session.get(SESSION_ANSWERS_KEY, {})
    accumulated_answers.update(normalized_answers)
    request.session[SESSION_ANSWERS_KEY] = accumulated_answers

    if step < TOTAL_STEPS:
        return RedirectResponse(url=f"/test/paso/{step + 1}", status_code=303)

    final_question_ids = [question["id"] for question in TEST_QUESTIONS]
    if any(question_id not in accumulated_answers for question_id in final_question_ids):
        return templates.TemplateResponse(
            "test_step.html",
            _build_step_context(
                request,
                step,
                error="Faltan respuestas de etapas anteriores. Volvé a comenzar el test.",
            ),
            status_code=400,
        )

    request.session.pop(SESSION_ANSWERS_KEY, None)
    return _render_result(request, accumulated_answers)
