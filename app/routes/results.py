"""Rutas de resultados vocacionales."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.services.recommendation_service import get_demo_recommendations
from app.services.scoring_service import get_demo_riasec_scores

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/resultado", tags=["results"])


@router.get("/demo", response_class=HTMLResponse)
async def demo_result(request: Request):
    """Resultado vocacional de ejemplo para validar la interfaz."""
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "scores": get_demo_riasec_scores(),
            "recommendations": get_demo_recommendations(),
        },
    )
