"""Debrief endpoint - post-encounter analysis."""

from fastapi import APIRouter, Depends
from ..models.feedback import DebriefRequest, DebriefResponse
from ..core.tutor import Tutor, get_tutor

router = APIRouter()


@router.post("", response_model=DebriefResponse)
async def get_debrief(
  request: DebriefRequest,
  tutor: Tutor = Depends(get_tutor),
) -> DebriefResponse:
  """
  Get Echo's post-encounter debrief.

  Use this when:
  - Encounter is complete
  - Learner wants comprehensive feedback
  - Reviewing a case for learning
  """
  return await tutor.debrief_encounter(request)
