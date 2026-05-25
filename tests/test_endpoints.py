"""Smoke tests for Echo's HTTP endpoints (W3.8).

Mocks the Anthropic client so tests never touch the real API. Verifies
happy-path responses plus the global exception handler translation of
anthropic.APIStatusError and anthropic.APIConnectionError into structured
JSON the Metis portal can render.
"""

import os
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

# Set a dummy API key BEFORE importing Echo so Settings() validates
# and the startup() guard doesn't sys.exit(1) during TestClient bootstrap.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-used")

import anthropic  # noqa: E402
import httpx  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.main import app  # noqa: E402
from src.core.tutor import get_tutor  # noqa: E402
from src.models.feedback import QuestionResponse  # noqa: E402
from src.cases.models import (  # noqa: E402
  CasePhase,
  CaseState,
  GeneratedPatient,
  LearnerLevel,
  VisitType,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_status_error(status_code: int = 429, message: str = "rate limited") -> anthropic.APIStatusError:
  """Build a real APIStatusError with a synthetic httpx.Response."""
  request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
  response = httpx.Response(
    status_code=status_code,
    headers={"retry-after": "5"},
    request=request,
  )
  return anthropic.APIStatusError(message, response=response, body=None)


def _make_connection_error() -> anthropic.APIConnectionError:
  """Build a real APIConnectionError with a synthetic httpx.Request."""
  request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
  return anthropic.APIConnectionError(request=request)


def _make_case_state() -> CaseState:
  """Construct a minimal CaseState for /case/start/dynamic mocks."""
  return CaseState(
    patient=GeneratedPatient(
      name="Test Kid",
      age=24,
      age_unit="months",
      sex="female",
      weight_kg=12.5,
      chief_complaint="cough",
      parent_name="Parent",
      parent_style="anxious",
      condition_key="asthma",
      condition_display="Asthma Exacerbation",
      symptoms=["cough", "wheeze"],
      vitals={"hr": 110, "rr": 28, "temp_c": 37.2},
      exam_findings=[{"system": "resp", "finding": "wheeze"}],
    ),
    learner_level=LearnerLevel.STUDENT,
    visit_type=VisitType.SICK,
    phase=CasePhase.INTRO,
  )


@pytest.fixture
def client() -> AsyncIterator[TestClient]:
  """Yield a TestClient and reset dependency overrides after each test."""
  with TestClient(app) as c:
    yield c
  app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

def test_health_returns_200_with_expected_keys(client: TestClient) -> None:
  resp = client.get("/health")
  assert resp.status_code == 200
  body = resp.json()
  for key in (
    "status",
    "claude_configured",
    "eleven_labs_configured",
    "database_configured",
    "auth_enabled",
  ):
    assert key in body, f"missing key: {key}"
  assert body["status"] == "healthy"
  # We set ANTHROPIC_API_KEY at module load, so this must be True.
  assert body["claude_configured"] is True


# ---------------------------------------------------------------------------
# /question - happy path
# ---------------------------------------------------------------------------

def test_question_happy_path_returns_question_response(client: TestClient) -> None:
  """POST /question with a valid QuestionRequest returns a QuestionResponse."""
  canned = QuestionResponse(
    question="What's on your differential?",
    hint="Think about age + chief complaint.",
    topic="differential_diagnosis",
  )

  mock_tutor = MagicMock()
  mock_tutor.ask_socratic_question = AsyncMock(return_value=canned)
  app.dependency_overrides[get_tutor] = lambda: mock_tutor

  resp = client.post(
    "/question",
    json={
      "learner_question": "What should I do next?",
      "learner_level": "student",
    },
  )

  assert resp.status_code == 200, resp.text
  body = resp.json()
  assert body["question"] == canned.question
  assert body["hint"] == canned.hint
  assert body["topic"] == canned.topic
  mock_tutor.ask_socratic_question.assert_awaited_once()


# ---------------------------------------------------------------------------
# /question - APIStatusError translates to claude_api_error
# ---------------------------------------------------------------------------

def test_question_translates_anthropic_status_error(client: TestClient) -> None:
  """When the tutor raises anthropic.APIStatusError, the global handler
  in src/main.py returns structured JSON with error='claude_api_error'
  and preserves the upstream status code."""
  err = _make_status_error(status_code=429, message="rate limited")
  mock_tutor = MagicMock()
  mock_tutor.ask_socratic_question = AsyncMock(side_effect=err)
  app.dependency_overrides[get_tutor] = lambda: mock_tutor

  resp = client.post(
    "/question",
    json={"learner_question": "Help", "learner_level": "student"},
  )

  assert resp.status_code == 429
  body = resp.json()
  assert body["error"] == "claude_api_error"
  assert "message" in body
  assert body["retry_after"] == 5


# ---------------------------------------------------------------------------
# /question - APIConnectionError → 503 claude_api_unavailable
# ---------------------------------------------------------------------------

def test_question_translates_anthropic_connection_error(client: TestClient) -> None:
  """anthropic.APIConnectionError → 503 + error='claude_api_unavailable'."""
  err = _make_connection_error()
  mock_tutor = MagicMock()
  mock_tutor.ask_socratic_question = AsyncMock(side_effect=err)
  app.dependency_overrides[get_tutor] = lambda: mock_tutor

  resp = client.post(
    "/question",
    json={"learner_question": "Help", "learner_level": "student"},
  )

  assert resp.status_code == 503
  body = resp.json()
  assert body["error"] == "claude_api_unavailable"
  assert body["retry_after"] == 30


# ---------------------------------------------------------------------------
# /case/start/dynamic - smoke
# ---------------------------------------------------------------------------

def test_case_start_dynamic_smoke(client: TestClient) -> None:
  """/case/start/dynamic should call the dynamic generator + tutor opening
  and return a CaseResponse with the opening message echoed back."""
  case_state = _make_case_state()
  framework = {"topic": "Asthma", "images": []}

  mock_generator = MagicMock()
  mock_generator.generate_case = AsyncMock(return_value=case_state)
  mock_generator.get_framework = MagicMock(return_value=framework)

  # The router instantiates Tutor() directly (not via Depends), so we patch
  # the class constructor in the router's import namespace.
  mock_tutor_instance = MagicMock()
  mock_tutor_instance.generate_case_opening = AsyncMock(
    return_value="Hi, I'm bringing in my 2-year-old with a cough."
  )

  with patch(
    "src.cases.router.get_dynamic_generator",
    return_value=mock_generator,
  ), patch(
    "src.core.tutor.Tutor",
    return_value=mock_tutor_instance,
  ):
    resp = client.post(
      "/case/start/dynamic",
      json={
        "learner_level": "student",
        "condition_key": "asthma",
        "visit_type": "sick",
      },
    )

  assert resp.status_code == 200, resp.text
  body = resp.json()
  assert body["message"].startswith("Hi, I'm bringing in")
  assert body["case_state"]["patient"]["condition_key"] == "asthma"
  mock_generator.generate_case.assert_awaited_once()
  mock_tutor_instance.generate_case_opening.assert_awaited_once()
