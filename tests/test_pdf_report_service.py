"""Tests for PDF report generation."""

import pytest

pytest.importorskip("reportlab")

from app.services.pdf_report_service import generate_result_pdf


def _sample_result_data():
    return {
        "participant": {"current_status": "Estudiante", "age": "18", "location": "Córdoba"},
        "display_name": "Ana",
        "percentages": {"R": 60, "I": 90, "A": 50, "S": 80, "E": 55, "C": 45},
        "top_dimensions": [
            {"code": "I", "name": "Investigativo", "percentage": 90, "description": "Interés por investigar."},
            {"code": "S", "name": "Social", "percentage": 80, "description": "Interés por ayudar."},
            {"code": "R", "name": "Realista", "percentage": 60, "description": "Interés práctico."},
        ],
        "profile_code": "ISR",
        "insights": {
            "profile_summary": "Perfil orientado al análisis y a las personas.",
            "strengths": ["pensamiento analítico", "comunicación"],
            "work_environments": ["proyectos de investigación", "equipos colaborativos"],
            "next_steps": ["Comparar planes de estudio", "Hablar con profesionales"],
        },
        "recommended_careers": [
            {
                "name": "Ciencia de Datos",
                "match_percentage": 92,
                "area": "Tecnología",
                "duration": "4 años",
                "study_type": "Universitaria",
                "description": "Analiza información para resolver problemas.",
            }
        ],
    }


def test_generate_result_pdf_returns_bytes():
    pdf_bytes = generate_result_pdf(_sample_result_data())

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0


def test_generate_result_pdf_starts_with_valid_pdf_header():
    pdf_bytes = generate_result_pdf(_sample_result_data())

    assert pdf_bytes.startswith(b"%PDF")


def test_download_result_pdf_without_last_result_redirects_to_test():
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from app.main import app

    client = TestClient(app)

    response = client.get("/resultado/pdf", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/test"
