"""Rutas iniciales del test vocacional."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.data.questions import get_all_questions

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/test", tags=["test"])


@router.get("", response_class=HTMLResponse)
async def test_start(request: Request):
    """Pantalla inicial del test vocacional con preguntas RIASEC."""
    dimensions = {
        "R": "Realista",
        "I": "Investigativo",
        "A": "Artístico",
        "S": "Social",
        "E": "Emprendedor",
        "C": "Convencional",
    }
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
        for code, name in dimensions.items()
    ]
    likert_options = [
        (1, "No me interesa nada"),
        (2, "Me interesa poco"),
        (3, "Neutral"),
        (4, "Me interesa"),
        (5, "Me interesa mucho"),
    ]
    return templates.TemplateResponse(
        "test_start.html",
        {
            "request": request,
            "grouped_questions": grouped_questions,
            "likert_options": likert_options,
        },
    )
