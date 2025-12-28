"""Test Echo models."""

import pytest
from src.models import PatientContext, FeedbackRequest


def test_patient_context_age_display():
  """Test age display formatting."""
  # Years
  p = PatientContext(
    patient_id="123",
    source="oread",
    name="Test Patient",
    age_years=5,
  )
  assert p.age_display == "5 years"

  # Months
  p2 = PatientContext(
    patient_id="456",
    source="oread",
    name="Baby Test",
    age_months=8,
  )
  assert p2.age_display == "8 months"


def test_feedback_request_validation():
  """Test feedback request model."""
  patient = PatientContext(
    patient_id="123",
    source="mneme",
    name="Test Patient",
    age_years=3,
  )

  request = FeedbackRequest(
    patient=patient,
    learner_action="Ordered amoxicillin",
    action_type="medication_order",
    learner_level="student",
  )

  assert request.action_type == "medication_order"
  assert request.voice_response is False
