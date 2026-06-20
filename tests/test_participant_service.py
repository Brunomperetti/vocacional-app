"""Tests for optional participant data helpers."""

from app.services.participant_service import (
    clean_participant_data,
    get_display_name,
    validate_participant_data,
)


def test_clean_participant_data_strips_strings():
    participant = clean_participant_data(
        {
            "name": "  Ana  ",
            "email": " ana@example.com ",
            "age": " 18 ",
            "current_status": " Estoy en secundaria ",
            "location": " Córdoba ",
        }
    )

    assert participant == {
        "name": "Ana",
        "email": "ana@example.com",
        "age": "18",
        "current_status": "Estoy en secundaria",
        "location": "Córdoba",
    }


def test_invalid_email_returns_error_only_when_entered():
    assert validate_participant_data({"email": "", "age": ""}) == []
    errors = validate_participant_data({"email": "correo-invalido", "age": ""})

    assert any("email válido" in error for error in errors)


def test_age_out_of_range_returns_error_only_when_entered():
    assert validate_participant_data({"email": "", "age": ""}) == []
    errors = validate_participant_data({"email": "", "age": "99"})

    assert any("12 y 80" in error for error in errors)


def test_get_display_name_returns_name_or_fallback():
    assert get_display_name({"name": "  Ana "}) == "Ana"
    assert get_display_name({"name": ""}) == "Tu"
    assert get_display_name({}) == "Tu"
