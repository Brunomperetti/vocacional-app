"""Tests for reconstructing result data from session payloads."""

import pytest

from app.data.questions import TEST_QUESTIONS
from app.services.result_builder_service import build_result_from_session_data


def _complete_answers(value: str = "4") -> dict[str, str]:
    return {question["id"]: value for question in TEST_QUESTIONS}


def test_build_result_from_session_data_with_36_valid_answers():
    participant = {"name": "Ana", "age": "18", "current_status": "Terminé la secundaria"}

    result = build_result_from_session_data(participant, _complete_answers())

    assert result["participant"] == participant
    assert result["display_name"] == "Ana"
    assert set(result["percentages"]) == {"R", "I", "A", "S", "E", "C"}
    assert len(result["top_dimensions"]) == 3
    assert len(result["profile_code"]) == 3
    assert result["recommended_careers"]
    assert result["insights"]["profile_summary"]


def test_build_result_from_session_data_rejects_incomplete_answers():
    answers = _complete_answers()
    answers.pop(TEST_QUESTIONS[0]["id"])

    with pytest.raises(ValueError):
        build_result_from_session_data({}, answers)
