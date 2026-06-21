"""Tests for public informational pages."""

from fastapi.testclient import TestClient

from app.main import app


def test_privacy_page_responds_ok():
    client = TestClient(app)

    response = client.get("/privacidad")

    assert response.status_code == 200
    assert "Privacidad y uso de datos" in response.text


def test_legal_notice_page_responds_ok():
    client = TestClient(app)

    response = client.get("/aviso-legal")

    assert response.status_code == 200
    assert "Aviso importante" in response.text
