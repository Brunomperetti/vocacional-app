"""Rutas del test vocacional RIASEC por etapas."""

from urllib.parse import quote

import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.data.questions import TEST_QUESTIONS
from app.database import get_db
from app.services.participant_service import (
    CURRENT_STATUS_OPTIONS,
    clean_participant_data,
    validate_participant_data,
)
from app.services.result_builder_service import build_result_from_session_data
from app.services.result_persistence_service import save_test_result
from app.services.settings_service import get_app_name, get_donation_url, get_public_app_url
from app.services.scoring_service import DIMENSION_LABELS
from app.services.test_steps import (
    STEP_DIMENSIONS,
    TOTAL_STEPS,
    get_step_dimension_description,
    get_step_questions,
)

templates = Jinja2Templates(directory="app/templates")
templates.env.globals["get_app_name"] = get_app_name
router = APIRouter(prefix="/test", tags=["test"])
logger = logging.getLogger(__name__)

SESSION_ANSWERS_KEY = "answers"
SESSION_PARTICIPANT_KEY = "participant"


def _build_share_test_url(request: Request) -> str:
    """Arma el enlace de WhatsApp para compartir el test vocacional."""
    public_app_url = get_public_app_url()
    test_url = f"{public_app_url}/test" if public_app_url else str(request.url_for("test_start"))
    share_text = (
        "Hice un test vocacional gratuito y me dio un perfil con carreras recomendadas "
        f"según mis intereses. Podés probarlo acá: {test_url}"
    )
    return f"https://wa.me/?text={quote(share_text)}"


LIKERT_OPTIONS = [
    (1, "No me interesa nada"),
    (2, "Me interesa poco"),
    (3, "Neutral"),
    (4, "Me interesa"),
    (5, "Me interesa mucho"),
]


def _render_result(request: Request, answers: dict[str, str], db: Session | None = None) -> HTMLResponse:
    """Calcula y renderiza el resultado RIASEC final."""
    participant = request.session.get(SESSION_PARTICIPANT_KEY, {})
    result_data = build_result_from_session_data(participant, answers)

    if db is not None:
        try:
            test_result = save_test_result(db, participant, answers, result_data, request=request)
            request.session["last_result_id"] = test_result.id
        except Exception:
            logger.exception("No se pudo persistir el resultado del test vocacional.")
            db.rollback()

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "scores": result_data["percentages"],
            "top_dimensions": result_data["top_dimensions"],
            "profile_code": result_data["profile_code"],
            "recommendations": result_data["recommended_careers"],
            "insights": result_data["insights"],
            "is_demo": False,
            "participant": result_data["participant"],
            "display_name": result_data["display_name"],
            "donation_url": get_donation_url(),
            "whatsapp_share_url": _build_share_test_url(request),
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
        "donation_url": get_donation_url(),
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
            "donation_url": get_donation_url(),
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
                "donation_url": get_donation_url(),
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
async def process_test_step(request: Request, step: int, db: Session = Depends(get_db)):
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

    return _render_result(request, accumulated_answers, db)
