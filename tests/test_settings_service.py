"""Tests for environment-based settings helpers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.settings_service import get_donation_url, get_ga_measurement_id, get_meta_pixel_id, get_public_app_url


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


def test_get_app_name_returns_default_when_missing(monkeypatch):
    from app.services.settings_service import get_app_name

    monkeypatch.delenv("APP_NAME", raising=False)

    assert get_app_name() == "Vocación360"


def test_get_app_name_returns_configured_name(monkeypatch):
    from app.services.settings_service import get_app_name

    monkeypatch.setenv("APP_NAME", "Mi Test Vocacional")

    assert get_app_name() == "Mi Test Vocacional"


def test_base_template_uses_dynamic_app_name_in_header():
    html = Path("app/templates/base.html").read_text()

    assert '{{ get_app_name() }}' in html
    assert 'class="brand" href="/">{{ get_app_name() }}</a>' in html


def test_get_ga_measurement_id_returns_none_when_missing(monkeypatch):
    monkeypatch.delenv("GA_MEASUREMENT_ID", raising=False)

    assert get_ga_measurement_id() is None


def test_get_ga_measurement_id_returns_trimmed_value(monkeypatch):
    monkeypatch.setenv("GA_MEASUREMENT_ID", " G-ABC123 ")

    assert get_ga_measurement_id() == "G-ABC123"


def test_get_meta_pixel_id_returns_none_when_missing(monkeypatch):
    monkeypatch.delenv("META_PIXEL_ID", raising=False)

    assert get_meta_pixel_id() is None


def test_get_meta_pixel_id_returns_trimmed_value(monkeypatch):
    monkeypatch.setenv("META_PIXEL_ID", " 1234567890 ")

    assert get_meta_pixel_id() == "1234567890"


def test_base_template_contains_conditional_analytics_blocks():
    html = Path("app/templates/base.html").read_text()

    assert "{% if ga_measurement_id %}" in html
    assert 'gtag("config", "{{ ga_measurement_id }}")' in html
    assert "{% if meta_pixel_id %}" in html
    assert 'fbq("init", "{{ meta_pixel_id }}")' in html


def test_result_template_contains_tracking_data_attributes():
    html = Path("app/templates/result.html").read_text()

    assert 'data-track="download_pdf"' in html
    assert 'data-track="share_whatsapp"' in html
    assert 'data-track="donation_click"' in html


def test_test_step_template_contains_step_tracking_data_attributes():
    html = Path("app/templates/test_step.html").read_text()

    assert 'data-step-number="{{ step }}"' in html
    assert 'data-step-dimension="{{ dimension_code }}"' in html


def test_get_creator_linkedin_url_returns_none_when_missing(monkeypatch):
    from app.services.settings_service import get_creator_linkedin_url

    monkeypatch.delenv("CREATOR_LINKEDIN_URL", raising=False)

    assert get_creator_linkedin_url() is None


def test_get_creator_linkedin_url_returns_none_when_not_https(monkeypatch):
    from app.services.settings_service import get_creator_linkedin_url

    monkeypatch.setenv("CREATOR_LINKEDIN_URL", "http://linkedin.com/in/bruno")

    assert get_creator_linkedin_url() is None


def test_get_creator_linkedin_url_returns_trimmed_https_url(monkeypatch):
    from app.services.settings_service import get_creator_linkedin_url

    monkeypatch.setenv("CREATOR_LINKEDIN_URL", " https://www.linkedin.com/in/bruno-peretti ")

    assert get_creator_linkedin_url() == "https://www.linkedin.com/in/bruno-peretti"


def test_result_template_supports_testimonial_success_message():
    html = Path("app/templates/result.html").read_text()

    assert "comentario') == 'enviado'" in html
    assert "Gracias por dejar tu opinión" in html
    assert 'name="return_to"' in html


def test_index_template_contains_creator_section_with_conditional_linkedin_url():
    html = Path("app/templates/index.html").read_text()

    assert "CREADOR DEL PROYECTO" in html
    assert "Proyecto creado por Bruno Peretti" in html
    assert "{% if creator_linkedin_url %}" in html
    assert 'href="{{ creator_linkedin_url }}"' in html
