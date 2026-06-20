"""Smoke tests for the RIASEC scoring service."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.questions import TEST_QUESTIONS
from app.services.scoring_service import (
    build_profile_code,
    calculate_riasec_percentages,
    calculate_riasec_scores,
    get_top_dimensions,
)


def test_scoring_service_processes_complete_answers():
    answers = {}
    values_by_dimension = {"R": 3, "I": 5, "A": 4, "S": 2, "E": 1, "C": 3}
    for question in TEST_QUESTIONS:
        answers[question["id"]] = values_by_dimension[question["dimension"]]

    assert len(answers) == 36

    scores = calculate_riasec_scores(answers)
    percentages = calculate_riasec_percentages(scores)
    top_dimensions = get_top_dimensions(percentages)
    profile_code = build_profile_code(top_dimensions)

    assert all(0 <= percentage <= 100 for percentage in percentages.values())
    assert [dimension["code"] for dimension in top_dimensions] == ["I", "A", "R"]
    assert profile_code == "IAR"
    assert len(profile_code) == 3


if __name__ == "__main__":
    test_scoring_service_processes_complete_answers()
    print("Scoring service smoke test passed.")


def test_scoring_service_accepts_36_answers():
    answers = {question["id"]: "4" for question in TEST_QUESTIONS}

    scores = calculate_riasec_scores(answers)

    assert len(answers) == 36
    assert scores == {"R": 24, "I": 24, "A": 24, "S": 24, "E": 24, "C": 24}
