"""Static checks for the landing testimonial layout."""

from pathlib import Path


def test_landing_template_uses_testimonials_grid():
    template = Path("app/templates/index.html").read_text(encoding="utf-8")

    assert 'class="testimonials-section"' in template
    assert 'class="testimonials-grid"' in template


def test_testimonials_grid_aligns_cards_to_start():
    styles = Path("app/static/css/styles.css").read_text(encoding="utf-8")

    assert ".testimonials-grid" in styles
    assert "justify-content: start" in styles
    assert ".testimonials-grid {" in styles
    testimonials_grid_block = styles[
        styles.index(".testimonials-grid {"):styles.index(".testimonial-card {")
    ]
    assert "justify-content: center" not in testimonials_grid_block


def test_testimonials_have_mobile_layout_rules():
    styles = Path("app/static/css/styles.css").read_text(encoding="utf-8")

    assert "@media (max-width: 700px)" in styles
    assert ".testimonials-grid { grid-template-columns: 1fr; }" in styles
    assert ".testimonial-card { max-width: none; }" in styles


def test_testimonial_card_has_controlled_width():
    styles = Path("app/static/css/styles.css").read_text(encoding="utf-8")

    testimonial_card_block = styles[
        styles.index(".testimonial-card {"):styles.index(".testimonial-comment")
    ]
    assert "width: 100%" in testimonial_card_block
    assert "max-width: 420px" in testimonial_card_block
