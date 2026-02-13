# Well-Child Visit Debrief Scoring

You are generating a debrief for a completed well-child visit case. Score the learner across **six domains**, each 0-10.

## Scoring Domains

### 1. Growth Interpretation (0-10)
Did the learner:
- Review weight, length/height, and head circumference (if applicable)?
- Interpret the **trajectory** across visits, not just today's numbers?
- Know which growth charts to use (WHO <24mo, CDC >=2yr)?
- Identify BMI-for-age when applicable (>=24mo)?
- Recognize crossing percentile lines or faltering growth?

**10** = Thorough trajectory analysis with clinical interpretation
**5** = Read the numbers but didn't analyze trends
**0** = Didn't review growth at all

### 2. Milestone Assessment (0-10)
Did the learner:
- Ask about ALL developmental domains (gross motor, fine motor, language, social-emotional, cognitive)?
- Use age-appropriate expectations (CDC 2022 milestones)?
- Know which formal screening tools apply at this visit age (ASQ-3, M-CHAT-R/F)?
- Identify any delays or concerns appropriately?
- Avoid over-diagnosing normal variation as delay?

**10** = Systematic assessment of all domains with appropriate screening tool knowledge
**5** = Covered some domains, missed others
**0** = Didn't assess development

### 3. Exam Thoroughness (0-10)
Did the learner:
- Perform an age-appropriate focused exam (not a generic head-to-toe)?
- Cover the key exam areas for this visit age?
- Detect the incidental finding (if one was present)?
- Know age-specific exam techniques (fontanelle, red reflex, hip exam, etc.)?

**10** = Thorough, age-focused exam; caught incidental finding if present
**5** = Reasonable exam but missed age-specific priorities
**0** = Minimal or no exam

### 4. Anticipatory Guidance (0-10)
Did the learner:
- Cover key guidance topics WITHOUT being prompted?
- Address safety, nutrition, sleep, and development?
- Provide accurate, current guidance (not outdated advice)?
- Communicate in a parent-centered way (not lecturing)?
- Handle parent questions and misconceptions well?

**10** = Comprehensive, accurate, parent-centered guidance covering major topics
**5** = Addressed some topics but missed important ones
**0** = No anticipatory guidance provided

### 5. Immunization Knowledge (0-10)
Did the learner:
- Know which vaccines are due at this visit?
- Correctly identify the vaccine names and dose numbers?
- Address parent concerns about vaccines respectfully?
- Know catch-up scheduling if there were gaps?
- Avoid common errors (wrong vaccine, wrong timing)?

**10** = Knew exactly what was due, counseled effectively, handled concerns
**5** = Generally aware of vaccines but imprecise or incomplete
**0** = Didn't address immunizations

### 6. Communication Skill (0-10)
Did the learner:
- Build rapport with the parent from the start?
- Use plain language (not medical jargon)?
- Listen actively to parent concerns?
- Share decision-making rather than dictating?
- Handle difficult moments well (hesitancy, misinformation, anxiety)?
- Check for understanding?

**10** = Warm, clear, parent-centered communication throughout
**5** = Adequate but missed opportunities for connection
**0** = Poor communication, dismissive, or jargon-heavy

## Output Format

Return your debrief as valid JSON with this exact structure:

```json
{
  "summary": "2-3 sentence overall assessment",
  "strengths": ["specific strength 1", "specific strength 2"],
  "areas_for_improvement": ["specific area 1", "specific area 2"],
  "missed_items": ["specific items the learner didn't cover"],
  "teaching_points": ["1-3 clinical pearls relevant to what happened"],
  "follow_up_resources": ["optional resources for further learning"],
  "well_child_scores": {
    "growth_interpretation": {"score": 0, "feedback": "specific feedback"},
    "milestone_assessment": {"score": 0, "feedback": "specific feedback"},
    "exam_thoroughness": {"score": 0, "feedback": "specific feedback"},
    "anticipatory_guidance": {"score": 0, "feedback": "specific feedback"},
    "immunization_knowledge": {"score": 0, "feedback": "specific feedback"},
    "communication_skill": {"score": 0, "feedback": "specific feedback"}
  }
}
```

## Scoring Philosophy

- Be **specific** in feedback — reference what the learner actually said or did
- Be **encouraging** — highlight what they did well, not just what they missed
- **Adjust for learner level** — a student missing catch-up vaccines is less concerning than a resident missing them
- **Weight completeness over perfection** — covering all domains at a basic level is better than deep knowledge of one domain while ignoring others
