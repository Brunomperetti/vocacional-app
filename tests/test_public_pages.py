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


def test_landing_shows_creator_section_without_linkedin_url(monkeypatch):
    monkeypatch.delenv("CREATOR_LINKEDIN_URL", raising=False)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Proyecto creado por Bruno Peretti" in response.text
    assert "CREADOR DEL PROYECTO" in response.text
    assert "Vocación360 fue creado como una herramienta gratuita" in response.text
    assert "Ver perfil de LinkedIn" not in response.text


def test_landing_shows_linkedin_button_with_valid_url(monkeypatch):
    monkeypatch.setenv("CREATOR_LINKEDIN_URL", "https://www.linkedin.com/in/bruno-peretti")
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Proyecto creado por Bruno Peretti" in response.text
    assert "Ver perfil de LinkedIn" in response.text
    assert "https://www.linkedin.com/in/bruno-peretti" in response.text
