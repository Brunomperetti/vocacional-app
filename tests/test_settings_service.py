"""Tests for environment-based settings helpers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.settings_service import get_donation_url, get_public_app_url


def test_get_donation_url_returns_none_when_missing(monkeypatch):
    monkeypatch.delenv("DONATION_URL", raising=False)

    assert get_donation_url() is None


def test_get_donation_url_returns_configured_value(monkeypatch):
    url = "https://www.mercadopago.com.ar/link-de-aporte"
    monkeypatch.setenv("DONATION_URL", url)

    assert get_donation_url() == url


def test_result_template_guards_donation_section_with_optional_url():
    html = Path("app/templates/result.html").read_text()

    assert "{% if donation_url %}" in html
    assert "Aportar voluntariamente" in html
    assert 'target="_blank"' in html
    assert 'rel="noopener noreferrer"' in html


def test_get_public_app_url_returns_none_when_missing(monkeypatch):
    monkeypatch.delenv("PUBLIC_APP_URL", raising=False)

    assert get_public_app_url() is None


def test_get_public_app_url_trims_spaces_and_trailing_slash(monkeypatch):
    monkeypatch.setenv("PUBLIC_APP_URL", " https://vocacional-app.onrender.com/ ")

    assert get_public_app_url() == "https://vocacional-app.onrender.com"
