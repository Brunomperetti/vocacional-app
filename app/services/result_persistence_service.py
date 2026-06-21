"""Persistencia de resultados completos del test vocacional."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from sqlalchemy.orm import Session
from starlette.requests import Request

from app.data.questions import TEST_QUESTIONS
from app.models import TestAnswer, TestResult

QUESTION_DIMENSIONS = {question["id"]: question["dimension"] for question in TEST_QUESTIONS}


def serialize_json(data: Any) -> str:
    """Serializa datos a JSON estable y compatible con SQLite/PostgreSQL."""
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def _empty_to_none(value: object) -> str | None:
    """Convierte strings vacíos en None para guardar campos opcionales."""
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _request_user_agent(request: Request | None) -> str | None:
    if request is None:
        return None
    return request.headers.get("user-agent")


def _request_ip_address(request: Request | None) -> str | None:
    if request is None or request.client is None:
        return None
    return request.client.host


def save_test_result(
    db: Session,
    participant: Mapping[str, object],
    answers: Mapping[str, object],
    result_data: Mapping[str, Any],
    request: Request | None = None,
) -> TestResult:
    """Guarda un resultado completo y sus respuestas individuales."""
    age_value = participant.get("age")
    age = int(age_value) if str(age_value or "").strip() else None

    test_result = TestResult(
        name=_empty_to_none(participant.get("name")),
        whatsapp=_empty_to_none(participant.get("whatsapp")),
        age=age,
        current_status=_empty_to_none(participant.get("current_status")),
        location=_empty_to_none(participant.get("location")),
        consent_accepted=bool(participant.get("consent_accepted")),
        profile_code=str(result_data["profile_code"]),
        percentages_json=serialize_json(result_data["percentages"]),
        top_dimensions_json=serialize_json(result_data["top_dimensions"]),
        recommended_careers_json=serialize_json(result_data["recommended_careers"]),
        insights_json=serialize_json(result_data["insights"]),
        user_agent=_request_user_agent(request),
        ip_address=_request_ip_address(request),
    )
    db.add(test_result)
    db.flush()

    for question_id, raw_value in answers.items():
        if question_id not in QUESTION_DIMENSIONS:
            continue
        db.add(
            TestAnswer(
                test_result_id=test_result.id,
                question_id=question_id,
                dimension=QUESTION_DIMENSIONS[question_id],
                value=int(raw_value),
            )
        )

    db.commit()
    db.refresh(test_result)
    return test_result
