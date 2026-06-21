"""Rutas de resultados vocacionales."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.services.participant_service import get_display_name
from app.services.pdf_report_service import generate_result_pdf
from app.services.profile_summary_service import build_result_insights
from app.services.recommendation_service import get_demo_recommendations
from app.services.result_builder_service import build_result_from_session_data
from app.services.settings_service import get_donation_url
from app.services.scoring_service import (
    build_profile_code,
    get_demo_riasec_scores,
    get_top_dimensions,
)

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/resultado", tags=["results"])


@router.get("/pdf")
async def download_result_pdf(request: Request):
    """Reconstruye y descarga el resultado vocacional de la sesión como PDF."""
    participant = request.session.get("participant")
    answers = request.session.get("answers")

    try:
        result_data = build_result_from_session_data(participant, answers)
    except ValueError:
        return RedirectResponse(url="/test", status_code=303)

    pdf_bytes = generate_result_pdf(result_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="informe-vocacional.pdf"'},
    )


@router.get("/demo", response_class=HTMLResponse)
async def demo_result(request: Request):
    """Resultado vocacional de ejemplo para validar la interfaz."""
    scores = get_demo_riasec_scores()
    top_dimensions = get_top_dimensions(scores)
    profile_code = build_profile_code(top_dimensions)
    recommendations = get_demo_recommendations()
    insights = build_result_insights(top_dimensions, profile_code, scores, recommendations)
    participant = {}
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "scores": scores,
            "top_dimensions": top_dimensions,
            "profile_code": profile_code,
            "recommendations": recommendations,
            "insights": insights,
            "is_demo": True,
            "participant": participant,
            "display_name": get_display_name(participant),
            "donation_url": get_donation_url(),
        },
    )
