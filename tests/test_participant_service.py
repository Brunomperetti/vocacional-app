"""Tests for optional participant data helpers."""

from app.services.participant_service import (
    clean_participant_data,
    get_display_name,
    normalize_whatsapp,
    validate_participant_data,
)


def test_clean_participant_data_strips_strings():
    participant = clean_participant_data(
        {
            "name": "  Ana  ",
            "whatsapp": " +54 9 11 1234-5678 ",
            "age": " 18 ",
            "current_status": " Estoy en secundaria ",
            "location": " Córdoba ",
        }
    )

    assert participant == {
        "name": "Ana",
        "whatsapp": "+5491112345678",
        "age": "18",
        "current_status": "Estoy en secundaria",
        "location": "Córdoba",
    }


def test_invalid_whatsapp_returns_error_only_when_entered():
    assert validate_participant_data({"whatsapp": "", "age": ""}) == []
    participant = clean_participant_data({"whatsapp": "abc-123", "age": ""})
    errors = validate_participant_data(participant)

    assert any("WhatsApp válido" in error for error in errors)


def test_valid_whatsapp_is_normalized():
    assert normalize_whatsapp(" +54 (9) 11-1234 5678 ") == "+5491112345678"
    participant = clean_participant_data({"whatsapp": " 351 555-1234 "})

    assert participant["whatsapp"] == "3515551234"
    assert validate_participant_data(participant) == []


def test_age_out_of_range_returns_error_only_when_entered():
    assert validate_participant_data({"whatsapp": "", "age": ""}) == []
    errors = validate_participant_data({"whatsapp": "", "age": "99"})

    assert any("12 y 80" in error for error in errors)


def test_get_display_name_returns_name_or_fallback():
    assert get_display_name({"name": "  Ana "}) == "Ana"
    assert get_display_name({"name": ""}) == "Tu"
    assert get_display_name({}) == "Tu"
