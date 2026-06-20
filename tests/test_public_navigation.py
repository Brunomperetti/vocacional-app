"""Tests for public navigation links."""

from pathlib import Path


def test_public_navigation_hides_demo_and_admin_links():
    html = Path("app/templates/base.html").read_text()

    assert 'href="/test"' in html
    assert 'href="/resultado/demo"' not in html
    assert 'href="/admin"' not in html
