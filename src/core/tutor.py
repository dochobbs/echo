"""Core tutor logic using Claude."""

from functools import lru_cache
from pathlib import Path
from typing import Optional
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

# Import these at the module level for type hints, but actual classes imported later
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from ..cases.models import CaseState, CasePhase, DescribeCaseState, DescribedCase


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


@lru_cache
def get_well_child_prompt() -> str:
  """Load and cache the well-child teaching prompt."""
  return load_prompt("well_child")


@lru_cache
def get_well_child_debrief_prompt() -> str:
  """Load and cache the well-child debrief prompt."""
  return load_prompt("well_child_debrief")


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

  def __init__(self, api_key: str = None, model: str = None):
    settings = get_settings()
    self.client = anthropic.Anthropic(api_key=api_key or settings.anthropic_api_key)
    self.model = model or settings.claude_model
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

  # ==================== CASE-BASED TEACHING METHODS ====================

  def _format_images_for_prompt(self, images: list) -> str:
    """Format available images for inclusion in the system prompt."""
    if not images:
      return "No images available for this condition."

    lines = []
    for img in images:
      phase = img.get("phase", "exam")
      caption = img.get("caption", "")
      key = img.get("key", "")
      lines.append(f"- [{phase}] {key}: {caption}")

    lines.append("")
    lines.append("Note: Images are shown to the learner automatically based on case phase.")
    lines.append("You can reference what an image shows (e.g., 'As you can see in the image...')")
    return "\n".join(lines)

  def _build_case_system_prompt(self, case_state: "CaseState", condition_info: dict) -> str:
    """Build a system prompt for case-based teaching with fluid voice."""
    from ..cases.models import VisitType
    if case_state.visit_type == VisitType.WELL_CHILD:
      return self._build_well_child_system_prompt(case_state, condition_info)

    patient = case_state.patient
    parent_styles = condition_info.get("parent_styles", [])

    # Handle both formats: list of dicts (old YAML) or list of strings (frameworks)
    parent_style_info = {"description": "Concerned parent", "sample_lines": []}
    if parent_styles:
      if isinstance(parent_styles[0], dict):
        # Old format: list of dicts with key, description, sample_lines
        parent_style_info = next(
          (s for s in parent_styles if s.get("key") == patient.parent_style),
          {"description": "Concerned parent", "sample_lines": []}
        )
      elif isinstance(parent_styles[0], str):
        # New framework format: just a list of style names
        if patient.parent_style in parent_styles:
          parent_style_info = {"description": patient.parent_style, "sample_lines": []}

    return f"""{self.system_prompt}

## CURRENT CASE

You are running a case with a learner. You will fluidly switch between:
- **Roleplay as the parent** ({patient.parent_name}, who is {parent_style_info.get('description', 'concerned')})
- **Teaching/attending voice** (when they need guidance or you want to highlight something)

Switch between these naturally - mid-response if needed. The learner should feel like they're talking to one brilliant, helpful attending who knows when to be the patient and when to step out and teach.

### Patient Details (HIDDEN from learner - reveal only as they discover)
- **Name**: {patient.name}
- **Age**: {patient.age} {patient.age_unit}
- **Sex**: {patient.sex}
- **Weight**: {patient.weight_kg} kg
- **Actual condition**: {patient.condition_display} (don't reveal - let them figure it out)

### Symptoms present: {', '.join(patient.symptoms)}
### Vitals: Temp {patient.vitals.get('temp_f', 98.6)}°F, HR {patient.vitals.get('heart_rate', 100)}, RR {patient.vitals.get('respiratory_rate', 20)}, SpO2 {patient.vitals.get('spo2', 98)}%
### Exam findings: {', '.join([f.get('finding', '') for f in patient.exam_findings])}

### Parent Voice Sample Lines:
{chr(10).join(['- ' + line for line in parent_style_info.get('sample_lines', [])])}

### Teaching Goals:
{chr(10).join(['- ' + goal for goal in condition_info.get('teaching_goals', [])])}

### Common Learner Mistakes to Watch For:
{chr(10).join(['- ' + mistake for mistake in condition_info.get('common_mistakes', condition_info.get('common_learner_mistakes', []))])}

### Red Flags (must not be missed):
{chr(10).join(['- ' + flag for flag in condition_info.get('red_flags', [])])}

### Clinical Pearls (high-yield points):
{chr(10).join(['- ' + pearl for pearl in condition_info.get('clinical_pearls', [])])}

### Key History Questions to Elicit:
{chr(10).join(['- ' + q for q in condition_info.get('key_history_questions', [])])}

### Key Exam Findings to Discover:
{chr(10).join(['- ' + f for f in condition_info.get('key_exam_findings', [])])}

### Treatment Principles:
{chr(10).join(['- ' + t for t in condition_info.get('treatment_principles', [])])}

### Available Teaching Images:
{self._format_images_for_prompt(condition_info.get('images', []))}

## Current Case Phase: {case_state.phase.value}

## CRITICAL RULES

1. **Stay in roleplay by default** - Respond as the parent unless you need to teach
2. **Reveal information only when asked** - Don't volunteer symptoms they haven't asked about
3. **Signal role switches naturally** - Use brief, conversational transitions
4. **Never interrogate** - After 2-3 questions from you, give support instead
5. **Celebrate insights** - "Nice thinking" when they make good connections
6. **Help when stuck** - Notice silence or confusion, offer to share what you'd consider

## ROLE TRANSITION PHRASES

When stepping OUT of parent roleplay into attending voice:
- "[Stepping out for a moment] That's exactly the question I'd want you to ask."
- "[Quick teaching point] Nice instinct there."
- "[Attending hat on] Let me highlight something..."
- "[Pause from the case] Think about what that symptom tells you."

When stepping BACK into parent roleplay:
- "[Back to mom] So doctor, what do you think is going on?"
- "[Resuming] Anyway, she's been so fussy..."
- Just continue as the parent - no transition needed if smooth

Keep transitions BRIEF - one short bracketed phrase, then your content. Don't over-explain the switch."""

  def _build_well_child_system_prompt(self, case_state: "CaseState", framework: dict) -> str:
    """Build system prompt for well-child case teaching."""
    patient = case_state.patient
    well_child_prompt = get_well_child_prompt()

    milestones_text = ""
    if framework.get("expected_milestones"):
      for domain, items in framework["expected_milestones"].items():
        if isinstance(items, list):
          milestones_text += f"\n**{domain}**: {', '.join(items)}"

    immunizations_text = ""
    for vax in framework.get("immunizations_due", []):
      immunizations_text += f"\n- {vax.get('vaccine', '')} (CVX {vax.get('cvx', '')})"

    guidance_text = ""
    for category, items in framework.get("anticipatory_guidance", {}).items():
      if isinstance(items, list):
        guidance_text += f"\n**{category}**: {', '.join(items[:3])}"

    exam_focus_text = ""
    for item in framework.get("physical_exam_focus", []):
      if isinstance(item, dict):
        exam_focus_text += f"\n- {item.get('area', '')}: {item.get('detail', '')}"
      elif isinstance(item, str):
        exam_focus_text += f"\n- {item}"

    incidental_text = ""
    if patient.incidental_finding:
      incidental_text = f"""
### INCIDENTAL FINDING (reveal during exam or parent_questions phase)
- **Finding**: {patient.incidental_finding.get('description', '')}
- **Age relevance**: {patient.incidental_finding.get('age_relevance', '')}
- Present this naturally — don't announce it. Let the learner discover it."""

    screening_tools = framework.get("screening_tools", [])
    screening_text = ""
    for s in screening_tools:
      if isinstance(s, dict):
        screening_text += f"\n- {s.get('tool', '')} ({s.get('when', '')})"
      elif isinstance(s, str):
        screening_text += f"\n- {s}"

    return f"""{self.system_prompt}

{well_child_prompt}

## CURRENT WELL-CHILD CASE

### Patient
- **Name**: {patient.name}
- **Visit Age**: {patient.visit_age_months} months
- **Sex**: {patient.sex}
- **Weight**: {patient.weight_kg} kg
- **Parent**: {patient.parent_name} (style: {patient.parent_style})

### Growth Data
{json.dumps(patient.growth_data, indent=2) if patient.growth_data else "Standard growth"}

### Expected Milestones for This Age
{milestones_text}

### Actual Milestone Status
{json.dumps(patient.milestones, indent=2) if patient.milestones else "Typical for age"}

### Immunizations Due at This Visit
{immunizations_text}

### Anticipatory Guidance Topics
{guidance_text}

### Physical Exam Focus Areas
{exam_focus_text}

### Teaching Goals
{chr(10).join(['- ' + g for g in framework.get('teaching_goals', [])])}

### Common Learner Mistakes
{chr(10).join(['- ' + m for m in framework.get('common_mistakes', [])])}

### Screening Tools for This Age
{screening_text}

{incidental_text}

## Current Phase: {case_state.phase.value}

## WELL-CHILD RULES
1. **No chief complaint** - This child is here for a routine check
2. **Play the parent** - Respond to questions as the parent would
3. **Don't volunteer information** - Let the learner drive the visit
4. **Track what they cover** - Note which guidance topics, milestones, and vaccines they address
5. **Incidental finding** - If present, reveal naturally during appropriate phase
6. **Celebrate thoroughness** - Praise when they remember important screenings or guidance topics"""

  async def generate_case_opening(self, case_state: "CaseState", condition_info: dict) -> str:
    """Generate the opening message for a case."""
    from ..cases.models import VisitType
    patient = case_state.patient

    if case_state.visit_type == VisitType.WELL_CHILD:
      prompt = f"""You're starting a well-child visit case with a {case_state.learner_level.value} learner.

The patient is {patient.name}, a {patient.age} {patient.age_unit} old {patient.sex}
here for their {condition_info.get('topic', 'well-child check')}.
The parent ({patient.parent_name}) is here and seems {patient.parent_style}.

Start the encounter:
1. Briefly set the scene (routine well-child visit, you're the attending)
2. Present as the parent bringing in the child for their check-up
3. Mention any specific parent concerns if they have them, otherwise say things are going well
4. End with something that invites them to take the lead on the visit

Keep it natural. No chief complaint — this child is here for a routine visit.
3-4 sentences max from the parent."""
    else:
      prompt = f"""You're starting a new case with a {case_state.learner_level.value} learner.

The patient is {patient.name}, a {patient.age} {patient.age_unit} old {patient.sex}.
The parent ({patient.parent_name}) is bringing them in with this chief complaint:

"{patient.chief_complaint}"

Start the encounter:
1. Briefly set the scene (you're the attending, they're the learner)
2. Present as the parent bringing in the child
3. Give the chief complaint in the parent's voice
4. End with something that invites them to take the lead

Keep it natural and conversational. No more than 3-4 sentences from the parent to start.
This is their first interaction - make it feel welcoming and zero-pressure."""

    system = self._build_case_system_prompt(case_state, condition_info)

    response = self.client.messages.create(
      model=self.model,
      max_tokens=512,
      system=system,
      messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text

  def _detect_stuck(self, message: str, case_state: "CaseState") -> bool:
    """Detect if the learner seems stuck based on their message patterns.

    Signs of being stuck:
    - Very short responses (< 10 chars)
    - Confusion phrases ("I don't know", "not sure", "help")
    - Repetitive questions about what to do
    - Long gaps between messages (tracked elsewhere)
    """
    msg_lower = message.lower().strip()

    # Very short response
    if len(msg_lower) < 10:
      return True

    # Confusion indicators
    stuck_phrases = [
      "i don't know",
      "i'm not sure",
      "not sure",
      "what should i",
      "what do i",
      "help",
      "stuck",
      "confused",
      "no idea",
      "can you help",
      "i'm lost",
      "what now",
      "um",
      "uh",
      "?",  # Just a question mark
    ]

    for phrase in stuck_phrases:
      if phrase in msg_lower:
        return True

    # Check for pattern of short responses in recent conversation
    recent_user_msgs = [
      turn["content"] for turn in case_state.conversation[-6:]
      if turn["role"] == "user"
    ]

    if len(recent_user_msgs) >= 2:
      avg_len = sum(len(m) for m in recent_user_msgs) / len(recent_user_msgs)
      if avg_len < 20:
        return True

    return False

  async def process_case_message(
    self,
    message: str,
    case_state: "CaseState",
    condition_info: dict,
  ) -> tuple[str, "CaseState", Optional[str], bool]:
    """Process a learner message during a case.

    Returns (response, updated_case_state, optional_teaching_moment, hint_offered)
    """
    # Detect if learner seems stuck
    is_stuck = self._detect_stuck(message, case_state)

    # Build conversation history for context
    messages = []
    for turn in case_state.conversation:
      role = "user" if turn["role"] == "user" else "assistant"
      messages.append({"role": role, "content": turn["content"]})

    # Add the current message
    messages.append({"role": "user", "content": message})

    # Detect phase transitions and update state
    updated_state = self._update_case_phase(message, case_state)

    # Build prompt based on current phase
    phase_guidance = self._get_phase_guidance(updated_state.phase)

    # Add stuck guidance if detected
    stuck_guidance = ""
    if is_stuck:
      stuck_guidance = """

IMPORTANT: The learner seems stuck or uncertain. Shift into supportive attending mode:
- Don't ask another question - give them something to work with
- Offer a helpful frame: "Here's how I might think about this..."
- Or give a gentle nudge: "What if we consider..."
- Keep it warm and supportive - no shame for being stuck
- You might say something like: "Let me share what I'd be thinking at this point..."

CRITICAL: After giving your hint or guidance, STOP. Do not continue the conversation.
- Do NOT have the parent ask a follow-up question
- Do NOT roleplay the parent asking something else
- End your response after the teaching moment
- Wait for the learner to respond before continuing the case
"""
      updated_state.hints_given += 1

    prompt_prefix = f"""[Current phase: {updated_state.phase.value}]
{phase_guidance}
{stuck_guidance}
The learner says: "{message}"

Respond naturally - as the parent, as a teaching attending, or fluidly between both.
If they're asking questions, answer in character as the parent.
If they're making clinical decisions, you can slide into attending voice to comment.

Remember: help, don't interrogate."""

    messages[-1] = {"role": "user", "content": prompt_prefix}

    system = self._build_case_system_prompt(updated_state, condition_info)

    response = self.client.messages.create(
      model=self.model,
      max_tokens=1024,
      system=system,
      messages=messages,
    )

    response_text = response.content[0].text

    # Extract any teaching moment (for tracking, not shown separately)
    teaching_moment = None
    if "[TEACHING:" in response_text:
      # Extract and clean
      match = re.search(r'\[TEACHING:(.*?)\]', response_text)
      if match:
        teaching_moment = match.group(1).strip()
        updated_state.teaching_moments.append(teaching_moment)
        response_text = re.sub(r'\[TEACHING:.*?\]', '', response_text).strip()

    return response_text, updated_state, teaching_moment, is_stuck

  def _update_case_phase(self, message: str, case_state: "CaseState") -> "CaseState":
    """Update case phase based on learner's message."""
    from ..cases.models import CasePhase, VisitType

    if case_state.visit_type == VisitType.WELL_CHILD:
      return self._update_well_child_phase(message, case_state)

    msg_lower = message.lower()

    # Simple phase detection - can be made more sophisticated
    if case_state.phase == CasePhase.INTRO:
      # Any substantive question moves to history
      if any(word in msg_lower for word in ["when", "how long", "fever", "pain", "eating", "sleeping", "happened"]):
        case_state.phase = CasePhase.HISTORY

    elif case_state.phase == CasePhase.HISTORY:
      # Exam-related words move to exam phase
      if any(word in msg_lower for word in ["examine", "look at", "check", "ears", "throat", "lungs", "heart", "belly"]):
        case_state.phase = CasePhase.EXAM

    elif case_state.phase == CasePhase.EXAM:
      # Assessment words
      if any(word in msg_lower for word in ["think", "diagnosis", "differential", "could be", "looks like", "probably"]):
        case_state.phase = CasePhase.ASSESSMENT

    elif case_state.phase == CasePhase.ASSESSMENT:
      # Plan words
      if any(word in msg_lower for word in ["prescribe", "give", "recommend", "treat", "plan", "antibiotic", "medicine"]):
        case_state.phase = CasePhase.PLAN

    return case_state

  def _update_well_child_phase(self, message: str, case_state: "CaseState") -> "CaseState":
    """Update well-child case phase based on learner's message."""
    from ..cases.models import CasePhase
    msg_lower = message.lower()

    if case_state.phase == CasePhase.INTRO:
      if any(w in msg_lower for w in ["growth", "weight", "percentile", "chart", "gaining", "length", "head circumference"]):
        case_state.phase = CasePhase.GROWTH_REVIEW
      elif any(w in msg_lower for w in ["milestone", "development", "rolling", "sitting", "walking", "talking", "words"]):
        case_state.phase = CasePhase.DEVELOPMENTAL_SCREENING

    elif case_state.phase == CasePhase.GROWTH_REVIEW:
      if any(w in msg_lower for w in ["milestone", "development", "rolling", "sitting", "walking", "talking", "babbl", "words", "screen"]):
        case_state.phase = CasePhase.DEVELOPMENTAL_SCREENING
        case_state.growth_reviewed = True

    elif case_state.phase == CasePhase.DEVELOPMENTAL_SCREENING:
      if any(w in msg_lower for w in ["examine", "look at", "check", "exam", "heart", "ears", "hips", "lungs", "belly", "reflex"]):
        case_state.phase = CasePhase.EXAM

    elif case_state.phase == CasePhase.EXAM:
      if any(w in msg_lower for w in ["safety", "sleep", "feeding", "nutrition", "car seat", "tummy time", "screen time", "guidance", "counsel", "anticipatory"]):
        case_state.phase = CasePhase.ANTICIPATORY_GUIDANCE

    elif case_state.phase == CasePhase.ANTICIPATORY_GUIDANCE:
      if any(w in msg_lower for w in ["vaccine", "immuniz", "shot", "dtap", "mmr", "pcv", "hep", "flu", "schedule"]):
        case_state.phase = CasePhase.IMMUNIZATIONS

    elif case_state.phase == CasePhase.IMMUNIZATIONS:
      if any(w in msg_lower for w in ["question", "concern", "anything else", "wrap up", "done", "follow up"]):
        case_state.phase = CasePhase.PARENT_QUESTIONS

    return case_state

  def _get_phase_guidance(self, phase: "CasePhase") -> str:
    """Get phase-specific guidance for the tutor."""
    from ..cases.models import CasePhase

    guidance = {
      # Sick visit phases
      CasePhase.INTRO: "The learner is just starting. Let them take the lead.",
      CasePhase.HISTORY: "They're gathering history. Answer their questions as the parent would. Don't volunteer information they haven't asked about.",
      CasePhase.EXAM: "They want to examine. Describe what they find based on the exam findings. Be specific about normal and abnormal findings.",
      CasePhase.ASSESSMENT: "They're forming an assessment. Listen to their thinking. Gently probe if their differential is incomplete.",
      CasePhase.PLAN: "They're making a plan. Validate good choices, gently question problematic ones. Remember: shared decision-making with the parent matters.",
      CasePhase.DEBRIEF: "Time to debrief. Summarize what they did well and areas to improve.",
      CasePhase.COMPLETE: "The case is complete.",
      # Well-child phases
      CasePhase.GROWTH_REVIEW: "They're reviewing growth. See if they interpret trajectory, not just read numbers.",
      CasePhase.DEVELOPMENTAL_SCREENING: "They're assessing development. See if they cover all domains and know screening tools.",
      CasePhase.ANTICIPATORY_GUIDANCE: "They're counseling the parent. Don't prompt topics — see what they cover. Play the parent with realistic questions.",
      CasePhase.IMMUNIZATIONS: "They're addressing vaccines. See if they know what's due. If parent is hesitant, stay in character.",
      CasePhase.PARENT_QUESTIONS: "The parent has a question or concern. This may include an incidental finding. See how the learner handles it.",
    }
    return guidance.get(phase, "Continue the encounter naturally.")

  async def generate_well_child_debrief(self, case_state: "CaseState", framework: dict) -> dict:
    """Generate well-child debrief with domain scores."""
    patient = case_state.patient
    well_child_debrief_prompt = get_well_child_debrief_prompt()

    prompt = f"""{well_child_debrief_prompt}

## Case Summary
- **Visit**: {framework.get('topic', 'Well-Child Visit')}
- **Patient**: {patient.name}, {patient.age} {patient.age_unit}
- **Learner Level**: {case_state.learner_level.value}

## What the Learner Covered
- **Growth reviewed**: {case_state.growth_reviewed}
- **Milestones assessed**: {', '.join(case_state.milestones_assessed) if case_state.milestones_assessed else 'None documented'}
- **Guidance topics**: {', '.join(case_state.guidance_topics_covered) if case_state.guidance_topics_covered else 'None documented'}
- **Immunizations addressed**: {case_state.immunizations_addressed}
- **Screening tools used**: {', '.join(case_state.screening_tools_used) if case_state.screening_tools_used else 'None'}
- **Parent concerns addressed**: {', '.join(case_state.parent_concerns_addressed) if case_state.parent_concerns_addressed else 'None'}

## Expected at This Visit
- **Teaching goals**: {json.dumps(framework.get('teaching_goals', []))}
- **Immunizations due**: {json.dumps(framework.get('immunizations_due', []))}
- **Screening tools**: {json.dumps(framework.get('screening_tools', []))}
- **Anticipatory guidance**: {json.dumps(framework.get('anticipatory_guidance', {}))}

## Response Format
Return valid JSON only:
{{"summary": "2-3 sentences", "strengths": ["specific strengths"], "areas_for_improvement": ["specific areas"], "missed_items": ["what was missed"], "teaching_points": ["1-3 pearls"], "follow_up_resources": ["optional resources"], "well_child_scores": {{"growth_interpretation": {{"score": 0, "feedback": "specific feedback"}}, "milestone_assessment": {{"score": 0, "feedback": "..."}}, "exam_thoroughness": {{"score": 0, "feedback": "..."}}, "anticipatory_guidance": {{"score": 0, "feedback": "..."}}, "immunization_knowledge": {{"score": 0, "feedback": "..."}}, "communication_skill": {{"score": 0, "feedback": "..."}}}}}}"""

    response = self.client.messages.create(
      model=self.model,
      max_tokens=1500,
      system=self.system_prompt,
      messages=[{"role": "user", "content": prompt}]
    )

    content = clean_json_response(response.content[0].text)
    try:
      return json.loads(content)
    except json.JSONDecodeError:
      return {
        "summary": "Case complete.",
        "strengths": [],
        "areas_for_improvement": [],
        "missed_items": [],
        "teaching_points": [],
        "follow_up_resources": [],
        "well_child_scores": None,
      }

  async def generate_debrief(self, case_state: "CaseState", condition_info: dict) -> dict:
    """Generate end-of-case debrief with structured data.

    Returns a dict with: summary, strengths, areas_for_improvement,
    missed_items, teaching_points, follow_up_resources
    """
    from ..cases.models import VisitType
    if case_state.visit_type == VisitType.WELL_CHILD:
      return await self.generate_well_child_debrief(case_state, condition_info)

    patient = case_state.patient

    debrief_prompt = f"""The case is complete. Time for a debrief.

## Case Summary
- **Patient**: {patient.name}, {patient.age} {patient.age_unit} old
- **Condition**: {patient.condition_display}
- **Learner Level**: {case_state.learner_level.value}

## What Was Discovered
- **History gathered**: {', '.join(case_state.history_gathered) if case_state.history_gathered else 'Limited history'}
- **Exam performed**: {', '.join(case_state.exam_performed) if case_state.exam_performed else 'Limited exam'}
- **Differential considered**: {', '.join(case_state.differential) if case_state.differential else 'Not clearly stated'}
- **Plan proposed**: {', '.join(case_state.plan_proposed) if case_state.plan_proposed else 'Not clearly stated'}

## Teaching Goals for This Condition
{chr(10).join(['- ' + goal for goal in condition_info.get('teaching_goals', [])])}

## Clinical Pearls
{chr(10).join(['- ' + pearl for pearl in condition_info.get('clinical_pearls', [])])}

## Instructions

Provide a warm, encouraging debrief that helps them learn and grow.

Be specific:
- Reference actual things they said/did
- Explain WHY things matter, not just THAT they're important
- Share 1-2 clinical pearls they can use next time
- End the summary with a brief check-in

## Response Format

Return valid JSON only. No markdown, no code blocks:

{{"summary": "2-3 sentences capturing how the encounter went overall. End with a brief check-in: 'How did that feel?' or 'Anything you want to talk through?'", "strengths": ["Specific things done well - reference actual actions from the conversation"], "areas_for_improvement": ["Specific areas to work on - explain why it matters for patient care"], "missed_items": ["Things that should have been caught - if any, otherwise empty array"], "teaching_points": ["1-3 clinical pearls from this case that they can apply next time"], "follow_up_resources": ["Optional: relevant guidelines or resources - can be empty array"]}}"""

    response = self.client.messages.create(
      model=self.model,
      max_tokens=1024,
      system=self.system_prompt,
      messages=[{"role": "user", "content": debrief_prompt}]
    )

    content = clean_json_response(response.content[0].text)
    try:
      data = json.loads(content)
      return data
    except json.JSONDecodeError:
      # Fallback to unstructured response
      return {
        "summary": response.content[0].text,
        "strengths": [],
        "areas_for_improvement": [],
        "missed_items": [],
        "teaching_points": [],
        "follow_up_resources": [],
      }


  # ==================== DESCRIBE-A-CASE MODE ====================

  async def start_describe_session(self, learner_level: str) -> str:
    """Generate opening message for describe-a-case mode."""
    prompt = f"""A {learner_level} learner wants to discuss a case they've seen.

Your job: Be an engaged, curious attending who wants to hear about their case and help them learn from it.

Start with a warm invitation to tell you about the case. Something like:
- "I'd love to hear about it. Tell me what happened."
- "Sure, walk me through it. What brought the patient in?"

Keep it brief and welcoming. They should feel like you're genuinely interested, not testing them."""

    response = self.client.messages.create(
      model=self.model,
      max_tokens=256,
      system=self.system_prompt,
      messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text

  async def process_describe_message(
    self,
    message: str,
    state: "DescribeCaseState",
  ) -> tuple[str, "DescribeCaseState", Optional[list[dict]]]:
    """Process a message in describe-a-case mode.

    Returns: (response, updated_state, citations_if_any)
    """
    from ..cases.models import DescribeCasePhase
    from .citations import get_citation_search

    # Build conversation history
    messages = []
    for turn in state.conversation:
      role = "user" if turn["role"] == "user" else "assistant"
      messages.append({"role": role, "content": turn["content"]})

    messages.append({"role": "user", "content": message})

    # Determine phase and build appropriate prompt
    phase_prompt = self._get_describe_phase_prompt(message, state)

    # Check if we should search for citations
    citations = None
    citation_context = ""
    if self._should_search_citations(message, state):
      search = get_citation_search()
      # Extract topic from the case
      topic = self._extract_citation_topic(message, state)
      if topic:
        result = await search.search(topic, num_results=3)
        if result.citations:
          citations = [c.model_dump() for c in result.citations]
          state.citations.extend(citations)
          citation_context = self._format_citations_for_prompt(result.citations)

    # Build the prompt
    case_summary = self._summarize_described_case(state.case)

    prompt = f"""[Describe-a-case mode - Phase: {state.phase.value}]

## Case So Far
{case_summary if case_summary else "Just starting - learner hasn't shared details yet."}

## Current Message
Learner: "{message}"

{phase_prompt}

{citation_context}

## Remember
- Be curious, not testing
- Help them see what they did well
- If something seems off, explore it gently ("Tell me more about...")
- Share teaching points naturally, not as lectures
- If they're uncertain about something, help them reason through it"""

    messages[-1] = {"role": "user", "content": prompt}

    response = self.client.messages.create(
      model=self.model,
      max_tokens=1024,
      system=self.system_prompt,
      messages=messages,
    )

    response_text = response.content[0].text

    # Update phase based on conversation
    updated_state = self._update_describe_phase(message, state)

    return response_text, updated_state, citations

  def _get_describe_phase_prompt(self, message: str, state: "DescribeCaseState") -> str:
    """Get phase-specific guidance for describe mode."""
    from ..cases.models import DescribeCasePhase

    if state.phase == DescribeCasePhase.LISTENING:
      return """## Your Task
You're gathering the case. Ask follow-up questions to understand:
- The chief complaint and history
- Key exam findings
- What they were thinking (differential)
- What they did or planned to do

Be curious and engaged. "And then what happened?" "What were you thinking at that point?"
"""

    elif state.phase == DescribeCasePhase.DISCUSSING:
      return """## Your Task
You have enough of the case to discuss it. Focus on:
- What they did well (be specific)
- Any teaching opportunities (share insights, not criticisms)
- Alternative approaches they might consider
- Clinical pearls relevant to this case

Stay conversational. You're colleagues discussing an interesting case, not a formal evaluation."""

    elif state.phase == DescribeCasePhase.TEACHING:
      return """## Your Task
Time for focused teaching. Share:
- Key clinical pearls for this type of case
- Evidence-based guidelines if relevant
- Things to watch for next time

Keep it practical and memorable. They should leave with 2-3 things they'll actually use."""

    return "Continue the discussion naturally."

  def _update_describe_phase(self, message: str, state: "DescribeCaseState") -> "DescribeCaseState":
    """Update phase based on conversation progress."""
    from ..cases.models import DescribeCasePhase

    msg_lower = message.lower()

    # Transition from LISTENING to DISCUSSING once we have basic case info
    if state.phase == DescribeCasePhase.LISTENING:
      case = state.case
      # Have we gathered enough info?
      has_complaint = case.chief_complaint is not None or "came in" in msg_lower or "presented" in msg_lower
      has_details = len(case.key_history) > 0 or len(case.key_findings) > 0 or len(state.conversation) >= 4

      if has_complaint and has_details:
        state.phase = DescribeCasePhase.DISCUSSING

    elif state.phase == DescribeCasePhase.DISCUSSING:
      # Transition to TEACHING if they ask for teaching or we've discussed enough
      if any(phrase in msg_lower for phrase in ["what should i", "teach me", "guidelines", "evidence", "best practice"]):
        state.phase = DescribeCasePhase.TEACHING
      elif len(state.conversation) >= 10:  # After substantial discussion
        state.phase = DescribeCasePhase.TEACHING

    return state

  def _should_search_citations(self, message: str, state: "DescribeCaseState") -> bool:
    """Determine if we should search for citations."""
    msg_lower = message.lower()

    # Search if they ask about evidence, guidelines, or best practice
    evidence_triggers = [
      "evidence", "guideline", "protocol", "recommendation",
      "best practice", "standard of care", "what does the literature",
      "aap says", "cdc", "should i have"
    ]

    return any(trigger in msg_lower for trigger in evidence_triggers)

  def _extract_citation_topic(self, message: str, state: "DescribeCaseState") -> Optional[str]:
    """Extract a topic to search for citations."""
    case = state.case

    # Use chief complaint if available
    if case.chief_complaint:
      return case.chief_complaint

    # Otherwise try to extract from recent conversation
    if state.conversation:
      last_few = state.conversation[-3:]
      combined = " ".join([t.get("content", "") for t in last_few])
      # Simple extraction - could be more sophisticated
      if "fever" in combined.lower():
        return "pediatric fever management"
      if "ear" in combined.lower():
        return "acute otitis media treatment"
      if "cough" in combined.lower():
        return "pediatric cough evaluation"

    return None

  def _format_citations_for_prompt(self, citations: list) -> str:
    """Format citations for inclusion in prompt."""
    if not citations:
      return ""

    lines = ["## Relevant Evidence (you can reference these)"]
    for c in citations[:3]:
      lines.append(f"- **{c.source}**: {c.title}")
      if c.snippet:
        lines.append(f"  {c.snippet[:150]}...")

    return "\n".join(lines)

  def _summarize_described_case(self, case: "DescribedCase") -> str:
    """Summarize what we know about the described case."""
    from ..cases.models import DescribedCase

    parts = []
    if case.age_description:
      parts.append(f"**Patient**: {case.age_description}")
    if case.chief_complaint:
      parts.append(f"**Chief Complaint**: {case.chief_complaint}")
    if case.key_history:
      parts.append(f"**History**: {', '.join(case.key_history)}")
    if case.key_findings:
      parts.append(f"**Findings**: {', '.join(case.key_findings)}")
    if case.learner_assessment:
      parts.append(f"**Learner's Assessment**: {case.learner_assessment}")
    if case.learner_plan:
      parts.append(f"**Plan**: {case.learner_plan}")
    if case.actual_outcome:
      parts.append(f"**Outcome**: {case.actual_outcome}")

    return "\n".join(parts) if parts else ""

  # ==================== POST-DEBRIEF Q&A ====================

  async def answer_post_debrief_question(
    self,
    question: str,
    case_export: dict,
    previous_qa: list[dict] = None,
  ) -> dict:
    """Answer a follow-up question about a completed case.

    Args:
      question: The learner's question
      case_export: Full case export data (patient, conversation, debrief)
      previous_qa: Previous questions and answers in this conversation

    Returns:
      dict with answer, related_teaching_points, citations
    """
    previous_qa = previous_qa or []

    # Build case context
    patient = case_export.get("patient_summary", {})
    case_summary = case_export.get("case_summary", {})
    learning_materials = case_export.get("learning_materials", {})
    conversation = case_export.get("conversation_transcript", [])

    # Summarize the conversation (limit to key exchanges)
    convo_summary = []
    for msg in conversation[-20:]:  # Last 20 messages max
      role = "Learner" if msg.get("role") == "user" else "Echo"
      convo_summary.append(f"{role}: {msg.get('content', '')[:200]}...")

    # Build previous Q&A context
    prev_qa_text = ""
    if previous_qa:
      prev_qa_text = "\n## Previous Questions in This Session\n"
      for qa in previous_qa[-5:]:  # Last 5 Q&A pairs
        prev_qa_text += f"Q: {qa.get('question', '')}\nA: {qa.get('answer', '')}\n\n"

    prompt = f"""A learner has completed a case and is now asking a follow-up question during debrief review.

## Case Context
- **Patient**: {patient.get('name', 'Unknown')}, {patient.get('age', '?')} {patient.get('age_unit', '')}
- **Condition**: {case_export.get('condition_display', 'Unknown')}
- **Chief Complaint**: {patient.get('chief_complaint', 'Not recorded')}

## What the Learner Did
- **History gathered**: {', '.join(case_summary.get('history_gathered', [])) or 'Not recorded'}
- **Exam performed**: {', '.join(case_summary.get('exam_performed', [])) or 'Not recorded'}
- **Differential**: {', '.join(case_summary.get('differential', [])) or 'Not recorded'}
- **Plan proposed**: {', '.join(case_summary.get('plan_proposed', [])) or 'Not recorded'}

## Key Conversation Moments
{chr(10).join(convo_summary[-10:])}

## Teaching Points from This Case
{chr(10).join(['- ' + tp for tp in learning_materials.get('teaching_points', [])])}

## Clinical Pearls
{chr(10).join(['- ' + cp for cp in learning_materials.get('clinical_pearls', [])])}

{prev_qa_text}

## Learner's Question
"{question}"

## Your Task
Answer their question helpfully. You have full context of what happened in the case.

Guidelines:
- Be specific - reference what actually happened in the case
- If they're asking "why", explain the clinical reasoning
- If they're asking about alternatives, discuss trade-offs
- Keep it conversational, not lecture-y
- If the question relates to teaching points, reinforce them

## Response Format
Return valid JSON only:
{{"answer": "Your helpful response", "related_teaching_points": ["Any teaching points this reinforces"]}}"""

    response = self.client.messages.create(
      model=self.model,
      max_tokens=1024,
      system=self.system_prompt,
      messages=[{"role": "user", "content": prompt}]
    )

    content = clean_json_response(response.content[0].text)
    try:
      data = json.loads(content)
      return {
        "answer": data.get("answer", response.content[0].text),
        "related_teaching_points": data.get("related_teaching_points", []),
        "citations": None,
      }
    except json.JSONDecodeError:
      return {
        "answer": response.content[0].text,
        "related_teaching_points": [],
        "citations": None,
      }


@lru_cache
def get_tutor() -> Tutor:
  """Get cached tutor instance."""
  settings = get_settings()
  return Tutor(
    api_key=settings.anthropic_api_key,
    model=settings.claude_model,
  )
