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


# ==================== WELL-CHILD MODELS ====================

from src.cases.models import (
  VisitType, CasePhase, CaseState, GeneratedPatient,
  StartCaseRequest, DebriefData, WellChildScores,
)


def test_visit_type_enum():
  """VisitType has sick and well_child."""
  assert VisitType.SICK == "sick"
  assert VisitType.WELL_CHILD == "well_child"


def test_well_child_phases_exist():
  """Well-child phases are in CasePhase."""
  assert CasePhase.GROWTH_REVIEW == "growth_review"
  assert CasePhase.DEVELOPMENTAL_SCREENING == "developmental_screening"
  assert CasePhase.ANTICIPATORY_GUIDANCE == "anticipatory_guidance"
  assert CasePhase.IMMUNIZATIONS == "immunizations"
  assert CasePhase.PARENT_QUESTIONS == "parent_questions"


def test_generated_patient_optional_chief_complaint():
  """Well-child patients have no chief complaint."""
  patient = GeneratedPatient(
    name="Test Baby",
    age=2,
    age_unit="months",
    sex="female",
    weight_kg=5.0,
    parent_name="Mom",
    parent_style="anxious",
    condition_key="well_child_2mo",
    condition_display="2 Month Well-Child Visit",
    symptoms=[],
    vitals={"temp_f": 98.6},
    exam_findings=[],
    visit_age_months=2,
  )
  assert patient.chief_complaint is None
  assert patient.visit_age_months == 2


def test_case_state_well_child_defaults():
  """CaseState defaults to sick visit, well-child fields empty."""
  patient = GeneratedPatient(
    name="Test", age=2, age_unit="months", sex="male",
    weight_kg=5.0, chief_complaint="fever",
    parent_name="Mom", parent_style="anxious",
    condition_key="bronchiolitis", condition_display="Bronchiolitis",
    symptoms=["cough"], vitals={"temp_f": 101.0}, exam_findings=[],
  )
  state = CaseState(patient=patient)
  assert state.visit_type == VisitType.SICK
  assert state.growth_reviewed is False
  assert state.milestones_assessed == []
  assert state.guidance_topics_covered == []


def test_case_state_well_child_type():
  """CaseState can be set to well_child."""
  patient = GeneratedPatient(
    name="Baby", age=4, age_unit="months", sex="female",
    weight_kg=6.5, parent_name="Dad", parent_style="experienced",
    condition_key="well_child_4mo",
    condition_display="4 Month Well-Child Visit",
    symptoms=[], vitals={"temp_f": 98.6}, exam_findings=[],
    visit_age_months=4,
  )
  state = CaseState(
    patient=patient,
    visit_type=VisitType.WELL_CHILD,
    phase=CasePhase.GROWTH_REVIEW,
  )
  assert state.visit_type == VisitType.WELL_CHILD
  assert state.phase == CasePhase.GROWTH_REVIEW


def test_start_case_request_well_child():
  """StartCaseRequest accepts well_child visit type."""
  req = StartCaseRequest(
    visit_type=VisitType.WELL_CHILD,
    visit_age_months=12,
    learner_level="resident",
  )
  assert req.visit_type == VisitType.WELL_CHILD
  assert req.visit_age_months == 12


def test_well_child_scores_model():
  """WellChildScores has all six domains."""
  scores = WellChildScores(
    growth_interpretation={"score": 8, "feedback": "Good trajectory analysis"},
    milestone_assessment={"score": 7, "feedback": "Covered most domains"},
    exam_thoroughness={"score": 9, "feedback": "Age-appropriate exam"},
    anticipatory_guidance={"score": 6, "feedback": "Missed sleep safety"},
    immunization_knowledge={"score": 10, "feedback": "Perfect"},
    communication_skill={"score": 8, "feedback": "Warm and clear"},
  )
  assert scores.growth_interpretation.score == 8


def test_debrief_data_well_child_scores():
  """DebriefData can include well_child_scores."""
  debrief = DebriefData(
    summary="Good visit",
    well_child_scores=WellChildScores(
      growth_interpretation={"score": 8, "feedback": "Good"},
      milestone_assessment={"score": 7, "feedback": "Good"},
      exam_thoroughness={"score": 9, "feedback": "Good"},
      anticipatory_guidance={"score": 6, "feedback": "OK"},
      immunization_knowledge={"score": 10, "feedback": "Great"},
      communication_skill={"score": 8, "feedback": "Good"},
    ),
  )
  assert debrief.well_child_scores is not None
  assert debrief.well_child_scores.immunization_knowledge.score == 10
