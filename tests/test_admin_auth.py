"""Tests for simple admin authentication."""

from fastapi.testclient import TestClient

from app.auth import is_admin_configured, verify_admin_credentials
from app.main import app
from app.services.admin_service import safe_json_loads


def test_verify_admin_credentials_returns_true_for_correct_credentials(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "secret")

    assert verify_admin_credentials("admin", "secret") is True


def test_verify_admin_credentials_returns_false_for_wrong_credentials(monkeypatch):
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "secret")

    assert verify_admin_credentials("admin", "wrong") is False


def test_is_admin_configured_returns_false_if_variables_are_missing(monkeypatch):
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    assert is_admin_configured() is False


def test_admin_redirects_to_login_without_session():
    client = TestClient(app)

    response = client.get("/admin", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"


def test_admin_login_renders_without_breaking(monkeypatch):
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    client = TestClient(app)

    response = client.get("/admin/login")

    assert response.status_code == 200
    assert "Acceso administrador" in response.text
    assert "El acceso admin todavía no está configurado" in response.text


def test_admin_result_detail_redirects_to_login_without_session():
    client = TestClient(app)

    response = client.get("/admin/results/1", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"


def test_safe_json_loads_returns_fallback_for_invalid_json():
    fallback = {"ok": False}

    assert safe_json_loads("{invalid", fallback) == fallback
    assert safe_json_loads("", fallback) == fallback


def test_admin_export_csv_requires_admin_session():
    client = TestClient(app)

    response = client.get("/admin/export.csv", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"
