"""Tests for testimonial return URL handling."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.routes.testimonials import add_comment_status, sanitize_return_to


def test_sanitize_return_to_allows_internal_result_path():
    assert sanitize_return_to("/resultado") == "/resultado"


def test_sanitize_return_to_rejects_external_https_url():
    assert sanitize_return_to("https://malicioso.com") == "/"


def test_sanitize_return_to_uses_root_for_empty_value():
    assert sanitize_return_to("") == "/"


def test_add_comment_status_preserves_existing_query_params():
    assert add_comment_status("/resultado?foo=bar", "enviado") == "/resultado?foo=bar&comentario=enviado"
