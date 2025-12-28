"""Question endpoint - get Socratic questions from Echo."""

from fastapi import APIRouter, Depends
from ..models.feedback import QuestionRequest, QuestionResponse
from ..core.tutor import Tutor, get_tutor

router = APIRouter()


@router.post("", response_model=QuestionResponse)
async def get_question(
  request: QuestionRequest,
  tutor: Tutor = Depends(get_tutor),
) -> QuestionResponse:
  """
  Get a Socratic question from Echo.

  Use this when:
  - Learner asks for help ("What should I do?")
  - You want to prompt reflection on a case
  - Teaching moment during chart review
  """
  return await tutor.ask_socratic_question(request)
