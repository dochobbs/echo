"""Core tutor logic using Claude."""

from functools import lru_cache
from pathlib import Path
import anthropic
import json
import re

from ..config import get_settings
from ..models import PatientContext
from ..models.feedback import (
  FeedbackRequest, FeedbackResponse,
  QuestionRequest, QuestionResponse,
  DebriefRequest, DebriefResponse,
)


# Prompts directory
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(name: str) -> str:
  """Load a prompt template from the prompts directory."""
  path = PROMPTS_DIR / f"{name}.md"
  if not path.exists():
    raise FileNotFoundError(f"Prompt file not found: {path}")
  return path.read_text()


@lru_cache
def get_system_prompt() -> str:
  """Load and cache the system prompt."""
  return load_prompt("system")


def clean_json_response(text: str) -> str:
  """Strip markdown code blocks from LLM response."""
  text = re.sub(r'^```(?:json)?\s*\n?', '', text.strip())
  text = re.sub(r'\n?```\s*$', '', text.strip())
  return text.strip()


def format_patient_context(patient: PatientContext) -> str:
  """Format patient context for the prompt."""
  lines = [
    f"PATIENT: {patient.name}, {patient.age_display}, {patient.sex or 'sex unknown'}",
    f"Source: {patient.source}",
  ]

  if patient.problem_list:
    active = [c.display_name for c in patient.problem_list if c.is_active]
    if active:
      lines.append(f"Active Problems: {', '.join(active)}")

  if patient.medication_list:
    meds = [m.display_name for m in patient.medication_list if m.is_active]
    if meds:
      lines.append(f"Medications: {', '.join(meds)}")

  if patient.allergy_list:
    allergies = [f"{a.display_name} ({a.reaction})" if a.reaction else a.display_name
                 for a in patient.allergy_list]
    lines.append(f"ALLERGIES: {', '.join(allergies)}")

  if patient.recent_encounters:
    enc = patient.recent_encounters[0]
    lines.append(f"Last visit: {enc.date} - {enc.chief_complaint}")

  return "\n".join(lines)


class Tutor:
  """Claude-powered medical tutor."""

  def __init__(self, api_key: str, model: str):
    self.client = anthropic.Anthropic(api_key=api_key)
    self.model = model
    self.system_prompt = get_system_prompt()

  def _build_feedback_prompt(self, request: FeedbackRequest, patient_context: str) -> str:
    """Build the feedback prompt with patient context."""
    context_line = f"- **Additional Context**: {request.context}" if request.context else ""

    prompt = f"""## Patient Context
{patient_context}

## The Situation
- **Learner Level**: {request.learner_level}
- **Action Type**: {request.action_type}
- **What They Did**: {request.learner_action}
{context_line}

## Your Task

Provide feedback on this action. Think through:

1. **Clinical appropriateness**: Is this reasonable for this patient?
2. **Safety check**: Any allergies, contraindications, red flags?
3. **Reasoning**: What thinking led to this choice?
4. **Family impact**: How does this affect the child and parents?

## How to Respond

### If it's good:
- Say so directly: "Nice job", "I like how you're thinking about that"
- Don't over-elaborate
- You might add one deepening question, but don't interrogate

### If there's a problem:
- First understand: Is this a knowledge gap? Reasoning error? Overconfidence? Carelessness?
- For safety issues: Be direct but understated - "I'd review that again if I were you"
- For other issues: Help them see it - reframe, add context, compare options
- Never shame or make it a big deal

### If it's mixed:
- Acknowledge what's good first
- Then gently redirect: "One thing to consider..."

## Common Pediatric Pitfalls to Watch For

- Too quick to treat (vs. watchful waiting, reassurance, shared decision-making)
- Not considering how this affects the family
- Ignoring what the parent said or wanted
- Being too "medical" - jargon, losing the human
- Overconfidence about the "right" answer

## Response Format

Respond with valid JSON only. No markdown, no code blocks:

{{"feedback": "Your response to the learner - direct, helpful, not preachy", "feedback_type": "praise|correction|question|suggestion", "clinical_issue": "If there's a safety issue, state it clearly. Otherwise null", "follow_up_question": "Optional: One question to deepen thinking. Can be null if feedback is sufficient"}}"""

    return prompt

  def _build_question_prompt(self, request: QuestionRequest, patient_context: str) -> str:
    """Build the question prompt from template."""
    topic_line = f"- **Focus Topic**: {request.topic}" if request.topic else ""

    prompt = f"""A learner is asking you a question. Your job is to help them learn - not to quiz them.

## Patient Context
{patient_context}

## The Situation
- **Learner Level**: {request.learner_level}
- **Their Question**: {request.learner_question}
{topic_line}

## Your Task

Respond in a way that helps them learn. This does NOT mean always asking a question back.

## Decision Tree

### Is this their first question?
- You can ask a guiding question to understand their thinking
- Or provide helpful context and see where they go

### Have they already answered 2-3 questions from you?
- Default to giving more support, not another question
- A series of questions feels like an interrogation

### Are their responses getting short or flippant?
- They're frustrated - stop questioning
- Give them what they need to move forward

### Do they genuinely not know and need help?
- **For students/NP students**: "How might you find out?", "What tools do you use?"
- **For residents**: Present material or resources (not "go look it up")
- Sometimes just help them directly

## Techniques When They're Stuck

Instead of another question, try:
- **Reframe**: "What if it were X instead of Y?"
- **Add context**: "What if I told you Z?"
- **Compare**: "How does A compare to B?"
- **Just help**: Give them a piece of what they need

## Response Format

Respond with valid JSON only. No markdown, no code blocks:

{{"question": "Your helpful response - could be a question, guidance, information, or reframe", "hint": "Optional gentle nudge or additional context. Can be null", "topic": "The clinical concept this addresses"}}"""

    return prompt

  def _build_debrief_prompt(self, request: DebriefRequest, patient_context: str) -> str:
    """Build the debrief prompt from template."""
    enc = request.encounter

    known_errors_line = f"### Known Errors in Scenario\n{', '.join(enc.known_errors)}" if enc.known_errors else ""
    focus_areas_line = f"- **Focus Areas**: {', '.join(request.focus_areas)}" if request.focus_areas else ""

    prompt = f"""The encounter is over. Your job is to help the learner reflect and grow.

## Patient Context
{patient_context}

## The Encounter
- **Type**: {enc.encounter_type}
- **Chief Complaint**: {enc.chief_complaint}

### What They Did
- **History Gathered**: {', '.join(enc.history_gathered) if enc.history_gathered else 'none documented'}
- **Exam Findings**: {', '.join(enc.exam_findings) if enc.exam_findings else 'none documented'}
- **Differential**: {', '.join(enc.differential) if enc.differential else 'none documented'}
- **Orders/Plan**: {', '.join(enc.orders_placed) if enc.orders_placed else 'none'}

{known_errors_line}

## Learner Info
- **Level**: {request.learner_level}
{focus_areas_line}

## Debrief Principles

### Start with strengths
- What did they do well? Be specific.
- "Nice job asking about the fever history" not "Good history taking"
- Direct praise, don't over-elaborate

### Be specific about improvements
- Reference actual missed items or suboptimal choices
- Explain *why* it matters, not just *that* it was wrong
- Connect to patient impact or family impact

### Watch for common pediatric issues
- Did they listen to the parent?
- Did they consider family impact?
- Were they too quick to treat vs. watchful waiting?
- Did they explain things in accessible language?
- Were they overconfident about the "right" answer?

### Teaching points should be useful
- 1-3 clinical pearls from this specific case
- Things they can apply next time
- Not generic textbook knowledge

### Tone
- Supportive, not judgmental
- They should leave wanting to see another patient, not feeling defeated
- Remember: success = they stay engaged and want to learn more

## Response Format

Respond with valid JSON only. No markdown, no code blocks:

{{"summary": "2-3 sentences capturing how the encounter went overall. End with a brief check-in.", "strengths": ["Specific things done well - reference actual actions"], "areas_for_improvement": ["Specific areas to work on - explain why it matters"], "missed_items": ["Things that should have been caught - if any, otherwise empty array"], "teaching_points": ["1-3 clinical pearls from this case"], "follow_up_resources": ["Optional: relevant guidelines, articles, or resources. Can be empty array"]}}"""

    return prompt

  async def provide_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
    """Provide feedback on a learner action."""
    patient_context = format_patient_context(request.patient)
    prompt = self._build_feedback_prompt(request, patient_context)

    response = self.client.messages.create(
      model=self.model,
      max_tokens=1024,
      system=self.system_prompt,
      messages=[{"role": "user", "content": prompt}]
    )

    content = clean_json_response(response.content[0].text)
    try:
      data = json.loads(content)
      return FeedbackResponse(**data)
    except json.JSONDecodeError:
      return FeedbackResponse(
        feedback=response.content[0].text,
        feedback_type="suggestion",
      )

  async def ask_socratic_question(self, request: QuestionRequest) -> QuestionResponse:
    """Generate a helpful response to learner question."""
    normalized_patient = request.get_normalized_patient()
    patient_context = format_patient_context(normalized_patient) if normalized_patient else "No patient context provided."
    prompt = self._build_question_prompt(request, patient_context)

    response = self.client.messages.create(
      model=self.model,
      max_tokens=512,
      system=self.system_prompt,
      messages=[{"role": "user", "content": prompt}]
    )

    content = clean_json_response(response.content[0].text)
    try:
      data = json.loads(content)
      return QuestionResponse(**data)
    except json.JSONDecodeError:
      return QuestionResponse(
        question=response.content[0].text,
        topic="clinical reasoning",
      )

  async def debrief_encounter(self, request: DebriefRequest) -> DebriefResponse:
    """Provide post-encounter debrief."""
    patient_context = format_patient_context(request.patient)
    prompt = self._build_debrief_prompt(request, patient_context)

    response = self.client.messages.create(
      model=self.model,
      max_tokens=2048,
      system=self.system_prompt,
      messages=[{"role": "user", "content": prompt}]
    )

    content = clean_json_response(response.content[0].text)
    try:
      data = json.loads(content)
      return DebriefResponse(**data)
    except json.JSONDecodeError:
      return DebriefResponse(
        summary=response.content[0].text,
        strengths=[],
        areas_for_improvement=[],
        missed_items=[],
        teaching_points=[],
      )


@lru_cache
def get_tutor() -> Tutor:
  """Get cached tutor instance."""
  settings = get_settings()
  return Tutor(
    api_key=settings.anthropic_api_key,
    model=settings.claude_model,
  )
