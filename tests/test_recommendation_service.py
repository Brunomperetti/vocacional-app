"""Tests for the RIASEC career recommendation service."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.data.careers import CAREERS, RIASEC_DIMENSIONS
from app.services.recommendation_service import recommend_careers


def test_initial_career_database_has_at_least_40_complete_riasec_profiles():
    assert len(CAREERS) >= 40

    for career in CAREERS:
        profile = career["riasec_profile"]
        assert set(profile) == set(RIASEC_DIMENSIONS)
        assert all(1 <= profile[dimension] <= 5 for dimension in RIASEC_DIMENSIONS)


def test_recommend_careers_returns_ordered_valid_match_percentages():
    user_percentages = {"R": 20, "I": 100, "A": 40, "S": 40, "E": 60, "C": 100}

    recommendations = recommend_careers(user_percentages, limit=8)
    match_percentages = [item["match_percentage"] for item in recommendations]

    assert len(recommendations) == 8
    assert match_percentages == sorted(match_percentages, reverse=True)
    assert all(0 <= percentage <= 100 for percentage in match_percentages)
