"""Tests for the RIASEC test wizard steps."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.test_steps import STEP_DIMENSIONS, get_step_questions


def test_step_dimensions_define_six_riasec_steps():
    assert STEP_DIMENSIONS == {
        1: "R",
        2: "I",
        3: "A",
        4: "S",
        5: "E",
        6: "C",
    }


def test_each_step_loads_six_questions_for_its_dimension():
    for step, dimension in STEP_DIMENSIONS.items():
        questions = get_step_questions(step)

        assert len(questions) == 6
        assert {question["dimension"] for question in questions} == {dimension}
