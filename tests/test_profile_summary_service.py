"""Tests for human-readable RIASEC result insights."""

from app.services.profile_summary_service import (
    build_result_insights,
    build_strengths,
    build_work_environments,
)

TOP_DIMENSIONS = [
    {"code": "I", "name": "Investigativo", "percentage": 88},
    {"code": "E", "name": "Emprendedor", "percentage": 76},
    {"code": "A", "name": "Artístico", "percentage": 70},
]
PERCENTAGES = {"R": 40, "I": 88, "A": 70, "S": 52, "E": 76, "C": 48}
RECOMMENDED_CAREERS = [
    {"name": "Ciencia de Datos", "match_percentage": 91},
    {"name": "Marketing Digital", "match_percentage": 87},
]


def test_build_result_insights_returns_expected_keys():
    insights = build_result_insights(TOP_DIMENSIONS, "IEA", PERCENTAGES, RECOMMENDED_CAREERS)

    assert set(insights) == {
        "profile_summary",
        "strengths",
        "work_environments",
        "next_steps",
        "percentages",
    }


def test_profile_summary_is_not_empty():
    insights = build_result_insights(TOP_DIMENSIONS, "IEA", PERCENTAGES, RECOMMENDED_CAREERS)

    assert insights["profile_summary"]


def test_strengths_returns_at_least_four_items():
    assert len(build_strengths(TOP_DIMENSIONS)) >= 4


def test_work_environments_returns_at_least_three_items():
    assert len(build_work_environments(TOP_DIMENSIONS)) >= 3


def test_next_steps_returns_at_least_four_items():
    insights = build_result_insights(TOP_DIMENSIONS, "IEA", PERCENTAGES, RECOMMENDED_CAREERS)

    assert len(insights["next_steps"]) >= 4
