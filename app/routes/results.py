"""Rutas de resultados vocacionales."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.profile_summary_service import build_result_insights
from app.services.recommendation_service import get_demo_recommendations
from app.services.scoring_service import (
    build_profile_code,
    get_demo_riasec_scores,
    get_top_dimensions,
)

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/resultado", tags=["results"])


@router.get("/demo", response_class=HTMLResponse)
async def demo_result(request: Request):
    """Resultado vocacional de ejemplo para validar la interfaz."""
    scores = get_demo_riasec_scores()
    top_dimensions = get_top_dimensions(scores)
    profile_code = build_profile_code(top_dimensions)
    recommendations = get_demo_recommendations()
    insights = build_result_insights(top_dimensions, profile_code, scores, recommendations)
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
        },
    )
