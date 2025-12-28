"""Feedback endpoint - get feedback on learner actions."""

from fastapi import APIRouter, Depends
from ..models import FeedbackRequest, FeedbackResponse
from ..core.tutor import Tutor, get_tutor

router = APIRouter()


@router.post("", response_model=FeedbackResponse)
async def get_feedback(
  request: FeedbackRequest,
  tutor: Tutor = Depends(get_tutor),
) -> FeedbackResponse:
  """
  Get Echo's feedback on a learner action.

  Use this when:
  - Learner makes a clinical decision (order, diagnosis)
  - Learner asks a question during an encounter
  - Learner documents something in the chart
  """
  return await tutor.provide_feedback(request)
