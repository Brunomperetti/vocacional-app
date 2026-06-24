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
    assert "Vocación360 fue creado como una herramienta gratuita" in html
    assert "{% if creator_linkedin_url %}" in html
    assert 'href="{{ creator_linkedin_url }}"' in html


def test_index_template_contains_creator_section_outside_linkedin_condition():
    html = Path("app/templates/index.html").read_text()
    section_start = html.index('<section id="creador" class="creator-section">')
    section_end = html.index('</section>', section_start)
    section = html[section_start:section_end]
    before_section = html[:section_start]

    assert "<!-- Creator section -->" in html
    assert "Proyecto creado por Bruno Peretti" in section
    assert "CREADOR DEL PROYECTO" in section
    assert "Vocación360 fue creado como una herramienta gratuita" in section
    assert "{% if creator_linkedin_url %}" not in before_section
    assert section.index("Proyecto creado por Bruno Peretti") < section.index("{% if creator_linkedin_url %}")


def test_index_template_shows_only_linkedin_button_conditionally():
    html = Path("app/templates/index.html").read_text()
    section_start = html.index('<section id="creador" class="creator-section">')
    section_end = html.index('</section>', section_start)
    section = html[section_start:section_end]

    assert "Ver perfil de LinkedIn" in section
    assert "{% if creator_linkedin_url %}" in section
    assert 'href="{{ creator_linkedin_url }}"' in section
    assert section.count("{% if creator_linkedin_url %}") == 1


def test_public_index_route_renders_index_with_public_context():
    source = Path("app/routes/public.py").read_text()

    assert '@router.get("/", response_class=HTMLResponse)' in source
    assert '"index.html"' in source
    assert "get_public_template_context" in source
    assert 'page="landing"' in source
    assert "testimonials=testimonials" in source


def test_creator_section_css_is_visible():
    css = Path("app/static/css/styles.css").read_text()
    section_rule_start = css.index(".creator-section")
    section_rule_end = css.index("}", section_rule_start)
    card_rule_start = css.index(".creator-card")
    card_rule_end = css.index("}", card_rule_start)
    creator_css = css[section_rule_start:section_rule_end] + css[card_rule_start:card_rule_end]

    assert "margin-top: 3rem" in creator_css
    assert "display: none" not in creator_css
    assert "visibility: hidden" not in creator_css
    assert "height: 0" not in creator_css
    assert "background: var(--card)" in creator_css
    assert "border: 1px solid var(--border)" in creator_css


def test_result_template_contains_structured_career_card_header():
    html = Path("app/templates/result.html").read_text()

    assert 'class="career-card-header"' in html
    assert 'class="career-card-title"' in html
    assert 'class="compatibility-badge"' in html
    assert html.index('class="career-card-header"') < html.index('class="compatibility-badge"') < html.index('class="career-card-meta"')


def test_result_template_contains_career_card_hierarchy_classes():
    html = Path("app/templates/result.html").read_text()

    assert 'class="career-card-meta"' in html
    assert 'class="career-card-description"' in html
    assert 'class="career-card-skills"' in html


def test_stylesheet_contains_responsive_career_grid_and_header_rules():
    css = Path("app/static/css/styles.css").read_text()

    assert ".career-cards" in css
    assert "repeat(auto-fit, minmax(280px, 1fr))" in css
    assert ".career-card-header" in css
    assert "flex-wrap: wrap" in css
    assert "@media (max-width: 700px)" in css
    assert ".career-card-header { align-items: flex-start; flex-direction: column; }" in css


def test_stylesheet_keeps_compatibility_badge_non_absolute():
    css = Path("app/static/css/styles.css").read_text()
    badge_rule_start = css.index(".compatibility-badge")
    badge_rule_end = css.index("}", badge_rule_start)
    badge_rule = css[badge_rule_start:badge_rule_end]

    assert "position: static" in badge_rule
    assert "display: inline-flex" in badge_rule
    assert "white-space: nowrap" in badge_rule
    assert "position: absolute" not in badge_rule
