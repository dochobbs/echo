"""Clinical guidelines lookup for Echo."""

from typing import Optional
from pydantic import BaseModel, Field


class Guideline(BaseModel):
  """Clinical guideline reference."""
  id: str
  title: str
  source: str  # "AAP", "CDC", "IDSA", etc.
  year: int
  condition: str
  summary: str
  key_points: list[str] = Field(default_factory=list)
  diagnostic_criteria: Optional[list[str]] = None
  treatment_recommendations: Optional[list[str]] = None
  red_flags: Optional[list[str]] = None
  url: Optional[str] = None


class GuidelineResult(BaseModel):
  """Result from guideline search."""
  guideline: Guideline
  relevance_score: float = 1.0
  matched_on: str = "condition"


# Clinical guidelines database
GUIDELINES: dict[str, Guideline] = {
  # Acute Otitis Media
  "aom_aap_2013": Guideline(
    id="aom_aap_2013",
    title="The Diagnosis and Management of Acute Otitis Media",
    source="AAP",
    year=2013,
    condition="acute_otitis_media",
    summary="Evidence-based guideline for AOM diagnosis and treatment in children 6 months to 12 years.",
    key_points=[
      "Diagnosis requires acute onset, middle ear effusion, and signs of middle ear inflammation",
      "Bulging tympanic membrane is the most important predictor of AOM",
      "Observation option appropriate for select children with non-severe AOM",
      "High-dose amoxicillin (80-90mg/kg/day) is first-line treatment",
      "Treatment failure defined as no improvement in 48-72 hours",
    ],
    diagnostic_criteria=[
      "Moderate to severe bulging of TM, OR",
      "New onset otorrhea not from otitis externa, OR",
      "Mild bulging of TM AND recent (<48h) ear pain/erythema",
    ],
    treatment_recommendations=[
      "Severe AOM or <6 months: Treat with antibiotics",
      "Non-severe, 6-23 months bilateral: Treat with antibiotics",
      "Non-severe, 6-23 months unilateral OR ≥2 years: Observe OR treat",
      "First-line: Amoxicillin 80-90mg/kg/day divided BID",
      "Penicillin allergy: Cefdinir, cefuroxime, or cefpodoxime",
      "Treatment failure: Amoxicillin-clavulanate or ceftriaxone IM",
    ],
    red_flags=[
      "Toxic appearance",
      "Persistent fever >39°C despite treatment",
      "Mastoid tenderness or swelling",
      "Facial nerve palsy",
      "Signs of meningitis",
    ],
    url="https://publications.aap.org/pediatrics/article/131/3/e964/30912",
  ),

  # Strep Pharyngitis
  "strep_idsa_2012": Guideline(
    id="strep_idsa_2012",
    title="Clinical Practice Guideline for GAS Pharyngitis",
    source="IDSA",
    year=2012,
    condition="strep_pharyngitis",
    summary="Guidelines for diagnosis and treatment of Group A Streptococcal pharyngitis.",
    key_points=[
      "Clinical features alone cannot distinguish GAS from viral pharyngitis",
      "Testing (rapid antigen or culture) required before treating",
      "Penicillin or amoxicillin remains first-line therapy",
      "Treatment prevents rheumatic fever if started within 9 days",
      "Carriers generally do not require treatment",
    ],
    diagnostic_criteria=[
      "Tonsillopharyngeal erythema with/without exudates",
      "Tender anterior cervical lymphadenopathy",
      "Fever",
      "Absence of cough, rhinorrhea, conjunctivitis (suggests viral)",
      "Positive rapid strep test OR throat culture",
    ],
    treatment_recommendations=[
      "First-line: Penicillin V 250mg BID-TID x10 days (weight <27kg)",
      "Alternative: Amoxicillin 50mg/kg once daily (max 1000mg) x10 days",
      "Penicillin allergy: Cephalexin, cefadroxil, clindamycin, or azithromycin",
      "Severe allergy (anaphylaxis): Azithromycin or clindamycin",
    ],
    red_flags=[
      "Respiratory distress or stridor",
      "Drooling or inability to swallow",
      "Trismus (difficulty opening mouth)",
      "Unilateral tonsillar swelling (peritonsillar abscess)",
      "Toxic appearance",
    ],
    url="https://www.idsociety.org/practice-guideline/pharyngitis/",
  ),

  # UTI
  "uti_aap_2011": Guideline(
    id="uti_aap_2011",
    title="UTI: Clinical Practice Guideline for Diagnosis and Management",
    source="AAP",
    year=2011,
    condition="urinary_tract_infection",
    summary="Guidelines for febrile UTI in children 2-24 months.",
    key_points=[
      "Diagnosis requires BOTH pyuria AND ≥50,000 CFU/mL of single uropathogen",
      "Catheterized or suprapubic specimen preferred over bag specimen",
      "Oral and parenteral antibiotics equally effective",
      "VCUG not routine after first febrile UTI if renal US is normal",
      "Renal ultrasound recommended after first febrile UTI",
    ],
    diagnostic_criteria=[
      "Pyuria: ≥10 WBC/HPF on enhanced UA OR positive leukocyte esterase",
      "Bacteriuria: ≥50,000 CFU/mL on catheter specimen",
      "Fever ≥38°C (100.4°F) with no other source",
    ],
    treatment_recommendations=[
      "Duration: 7-14 days (typically 7-10 days)",
      "Oral therapy if tolerating PO and not toxic",
      "Initial: Cephalexin, TMP-SMX, or amoxicillin-clavulanate",
      "Adjust based on culture sensitivities",
      "Follow-up urine culture not routinely needed if clinically improved",
    ],
    red_flags=[
      "Toxic appearance",
      "Severe dehydration",
      "Inability to tolerate oral intake",
      "Age <2 months (consider IV antibiotics)",
      "Concern for obstruction or abscess",
    ],
    url="https://publications.aap.org/pediatrics/article/128/3/595/30803",
  ),

  # Bronchiolitis
  "bronchiolitis_aap_2014": Guideline(
    id="bronchiolitis_aap_2014",
    title="Clinical Practice Guideline: Bronchiolitis",
    source="AAP",
    year=2014,
    condition="bronchiolitis",
    summary="Evidence-based management of bronchiolitis in children <2 years.",
    key_points=[
      "Bronchiolitis is a clinical diagnosis based on history and physical exam",
      "Routine diagnostic testing (CXR, labs, RSV testing) not recommended",
      "Supportive care is the mainstay: hydration and oxygen as needed",
      "Bronchodilators, steroids, and antibiotics NOT routinely recommended",
      "Nasal suctioning and supplemental O2 if SpO2 <90% persistently",
    ],
    diagnostic_criteria=[
      "Age <2 years",
      "First episode of wheezing",
      "Viral prodrome (rhinorrhea, cough, low-grade fever)",
      "Expiratory wheezing and/or crackles on exam",
      "Signs of respiratory distress variable",
    ],
    treatment_recommendations=[
      "Supportive care: fluids, nasal suctioning, supplemental O2 PRN",
      "Supplemental O2 if SpO2 persistently <90%",
      "NOT recommended routinely: albuterol, epinephrine, steroids, antibiotics",
      "Hypertonic saline may be considered for hospitalized patients",
      "High-flow nasal cannula for moderate-severe respiratory distress",
    ],
    red_flags=[
      "Apnea (especially in young infants <2 months)",
      "Severe respiratory distress (nasal flaring, retractions, grunting)",
      "SpO2 <90% on room air",
      "Poor feeding or dehydration",
      "Underlying cardiopulmonary disease or immunodeficiency",
    ],
    url="https://publications.aap.org/pediatrics/article/134/5/e1474/32947",
  ),

  # Asthma
  "asthma_naepp_2020": Guideline(
    id="asthma_naepp_2020",
    title="2020 Focused Updates to Asthma Guidelines",
    source="NAEPP/NHLBI",
    year=2020,
    condition="asthma",
    summary="Updated recommendations for asthma management including intermittent ICS and biologics.",
    key_points=[
      "Intermittent ICS-formoterol now preferred for mild persistent asthma (ages 4+)",
      "Short-course ICS at symptom onset for intermittent asthma",
      "Single maintenance and reliever therapy (SMART) recommended ages 4+",
      "Biologics recommended for severe, uncontrolled asthma with specific phenotypes",
      "Indoor allergen mitigation recommended as multicomponent approach",
    ],
    diagnostic_criteria=[
      "Recurrent episodes of wheeze, cough, dyspnea, chest tightness",
      "Symptoms worse at night or with triggers",
      "Reversible airflow obstruction on spirometry (if age appropriate)",
      "Family history of atopy often present",
    ],
    treatment_recommendations=[
      "Step 1 (Intermittent): PRN SABA; consider PRN low-dose ICS-formoterol",
      "Step 2 (Mild Persistent): Daily low-dose ICS OR PRN ICS-formoterol",
      "Step 3 (Moderate): Medium-dose ICS OR low-dose ICS-LABA",
      "Step 4+: Medium/high-dose ICS-LABA, consider add-on therapy",
      "Acute exacerbation: SABA, systemic corticosteroids",
    ],
    red_flags=[
      "Previous ICU admission or intubation for asthma",
      "≥2 hospitalizations or ≥3 ED visits in past year",
      "Using >2 SABA canisters per month",
      "Difficulty perceiving airflow obstruction",
      "Other comorbidities (psychiatric, cardiac)",
    ],
    url="https://www.nhlbi.nih.gov/health-topics/asthma",
  ),

  # Febrile Infant
  "febrile_infant_aap_2021": Guideline(
    id="febrile_infant_aap_2021",
    title="Evaluation and Management of Well-Appearing Febrile Infants 8-60 Days Old",
    source="AAP",
    year=2021,
    condition="febrile_infant",
    summary="Risk stratification approach for febrile infants based on age and inflammatory markers.",
    key_points=[
      "Age-stratified approach: 8-21 days, 22-28 days, 29-60 days",
      "Inflammatory markers (procalcitonin, ANC, CRP) aid risk stratification",
      "Low-risk infants 29-60 days may be managed without LP or hospitalization",
      "UTI is the most common serious bacterial infection in this age group",
      "HSV evaluation if risk factors or abnormal inflammatory markers",
    ],
    diagnostic_criteria=[
      "Temperature ≥38.0°C (100.4°F) rectally",
      "Age 8-60 days",
      "Well-appearing on exam",
      "No obvious source of infection",
    ],
    treatment_recommendations=[
      "8-21 days: LP, blood/urine cultures, empiric antibiotics, hospitalize",
      "22-28 days: Risk stratify; low-risk may avoid LP if normal markers",
      "29-60 days: Low-risk can be managed outpatient with close follow-up",
      "Empiric: Ampicillin + gentamicin (or cefotaxime); add acyclovir if HSV concern",
      "All require urine culture (cath or suprapubic)",
    ],
    red_flags=[
      "Ill-appearing",
      "Age <8 days (not covered by this guideline)",
      "Preterm (<37 weeks) or complex medical history",
      "Focal bacterial infection identified",
      "HSV risk factors (maternal history, vesicles, seizures)",
    ],
    url="https://publications.aap.org/pediatrics/article/148/2/e2021052228/179783",
  ),

  # Croup
  "croup_aap_2004": Guideline(
    id="croup_aap_2004",
    title="Diagnosis and Management of Croup",
    source="AAP",
    year=2004,
    condition="croup",
    summary="Clinical practice guideline for croup (laryngotracheobronchitis) management.",
    key_points=[
      "Croup is a clinical diagnosis; imaging rarely needed",
      "Westley Croup Score helps assess severity",
      "Dexamethasone is effective for all severity levels",
      "Nebulized epinephrine for moderate-severe croup",
      "Most children can be managed outpatient",
    ],
    diagnostic_criteria=[
      "Barky, seal-like cough",
      "Hoarseness",
      "Inspiratory stridor (at rest in moderate-severe)",
      "Age typically 6 months to 3 years",
      "Often preceded by URI symptoms",
    ],
    treatment_recommendations=[
      "Mild (stridor only with agitation): Dexamethasone 0.6mg/kg x1",
      "Moderate (stridor at rest): Dexamethasone + nebulized epinephrine",
      "Severe: Dexamethasone + repeated epinephrine + close monitoring",
      "Observe 2-4 hours after epinephrine before discharge",
      "Humidified air not proven effective but may comfort child",
    ],
    red_flags=[
      "Severe respiratory distress at rest",
      "Cyanosis or altered mental status",
      "No response to epinephrine",
      "Drooling or toxic appearance (consider epiglottitis)",
      "Recurrent or prolonged croup (consider other diagnoses)",
    ],
    url="https://publications.aap.org/pediatrics/article/114/4/1157/28653",
  ),

  # Constipation
  "constipation_naspghan_2014": Guideline(
    id="constipation_naspghan_2014",
    title="Evaluation and Treatment of Functional Constipation in Infants and Children",
    source="NASPGHAN/ESPGHAN",
    year=2014,
    condition="constipation",
    summary="Evidence-based recommendations for functional constipation management.",
    key_points=[
      "Diagnosis based on Rome IV criteria - no routine testing needed",
      "Red flags warrant further evaluation for organic causes",
      "Disimpaction before maintenance therapy",
      "PEG 3350 is first-line osmotic laxative",
      "Behavioral modification and toilet training support essential",
    ],
    diagnostic_criteria=[
      "Rome IV: ≥2 criteria for ≥1 month (infants/toddlers) or ≥2 months (children)",
      "≤2 defecations per week",
      "Excessive stool retention",
      "Painful or hard bowel movements",
      "Large diameter stools",
      "Fecal incontinence (if toilet trained)",
    ],
    treatment_recommendations=[
      "Disimpaction: PEG 1-1.5g/kg/day x3-6 days OR enemas",
      "Maintenance: PEG 0.4-0.8g/kg/day; titrate to soft daily stool",
      "Alternatives: Lactulose, mineral oil (>1 year), magnesium hydroxide",
      "Duration: Usually 3-6 months minimum, taper gradually",
      "Behavioral: Regular toilet sitting after meals, positive reinforcement",
    ],
    red_flags=[
      "Constipation since birth (Hirschsprung disease)",
      "Ribbon-like stools",
      "Failure to thrive",
      "Abdominal distension with vomiting",
      "Abnormal neurological exam or sacral abnormalities",
      "No meconium in first 48 hours of life",
    ],
    url="https://pubmed.ncbi.nlm.nih.gov/24345831/",
  ),
}


class GuidelineLookup:
  """Look up clinical guidelines by condition or keyword."""

  def __init__(self):
    self.guidelines = GUIDELINES

  def get_by_condition(self, condition: str) -> list[GuidelineResult]:
    """Get all guidelines for a condition."""
    results = []
    condition_lower = condition.lower().replace(" ", "_")

    for gid, guideline in self.guidelines.items():
      if condition_lower in guideline.condition.lower():
        results.append(GuidelineResult(
          guideline=guideline,
          relevance_score=1.0,
          matched_on="condition",
        ))

    return sorted(results, key=lambda x: x.guideline.year, reverse=True)

  def get_by_id(self, guideline_id: str) -> Optional[Guideline]:
    """Get specific guideline by ID."""
    return self.guidelines.get(guideline_id)

  def search(self, query: str) -> list[GuidelineResult]:
    """Search guidelines by keyword in title, summary, or key points."""
    results = []
    query_lower = query.lower()

    for gid, guideline in self.guidelines.items():
      score = 0.0
      matched_on = ""

      # Check title
      if query_lower in guideline.title.lower():
        score = max(score, 0.9)
        matched_on = "title"

      # Check condition
      if query_lower in guideline.condition.lower():
        score = max(score, 1.0)
        matched_on = "condition"

      # Check summary
      if query_lower in guideline.summary.lower():
        score = max(score, 0.7)
        matched_on = matched_on or "summary"

      # Check key points
      for point in guideline.key_points:
        if query_lower in point.lower():
          score = max(score, 0.6)
          matched_on = matched_on or "key_points"
          break

      if score > 0:
        results.append(GuidelineResult(
          guideline=guideline,
          relevance_score=score,
          matched_on=matched_on,
        ))

    return sorted(results, key=lambda x: x.relevance_score, reverse=True)

  def get_treatment_recommendations(self, condition: str) -> list[str]:
    """Get treatment recommendations for a condition."""
    guidelines = self.get_by_condition(condition)
    recommendations = []
    for result in guidelines:
      if result.guideline.treatment_recommendations:
        recommendations.extend(result.guideline.treatment_recommendations)
    return recommendations

  def get_red_flags(self, condition: str) -> list[str]:
    """Get red flags for a condition."""
    guidelines = self.get_by_condition(condition)
    flags = []
    for result in guidelines:
      if result.guideline.red_flags:
        flags.extend(result.guideline.red_flags)
    return list(set(flags))  # Deduplicate

  def list_conditions(self) -> list[str]:
    """List all conditions with available guidelines."""
    conditions = set()
    for guideline in self.guidelines.values():
      conditions.add(guideline.condition)
    return sorted(list(conditions))

  def list_all(self) -> list[Guideline]:
    """List all available guidelines."""
    return sorted(
      self.guidelines.values(),
      key=lambda x: (x.condition, -x.year),
    )
