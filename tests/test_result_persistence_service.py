"""Tests for database persistence of completed vocational results."""

import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.data.questions import TEST_QUESTIONS
from app.database import Base
from app.models import TestAnswer, TestResult
from app.services.result_builder_service import build_result_from_session_data
from app.services.result_persistence_service import save_test_result, serialize_json


def _session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def _answers(value="4"):
    return {question["id"]: value for question in TEST_QUESTIONS}


def test_serialize_json_keeps_valid_json_string():
    payload = {"b": ["Social", "Artístico"], "a": 1}

    serialized = serialize_json(payload)

    assert json.loads(serialized) == payload
    assert "Social" in serialized


def test_save_test_result_persists_result_and_36_answers():
    db = _session()
    participant = {
        "name": "Ana",
        "whatsapp": "+5491112345678",
        "age": "18",
        "current_status": "Terminé la secundaria",
        "location": "Córdoba",
        "consent_accepted": True,
    }
    answers = _answers()
    result_data = build_result_from_session_data(participant, answers)

    saved = save_test_result(db, participant, answers, result_data)

    stored = db.query(TestResult).filter_by(id=saved.id).one()
    assert stored.name == "Ana"
    assert stored.consent_accepted is True
    assert stored.profile_code == result_data["profile_code"]
    assert json.loads(stored.percentages_json) == result_data["percentages"]
    assert db.query(TestAnswer).filter_by(test_result_id=stored.id).count() == 36
