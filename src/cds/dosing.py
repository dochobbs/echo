"""Weight-based dosing calculator for pediatric medications."""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class DoseResult(BaseModel):
  """Calculated dose result."""
  medication: str
  indication: str
  dose_mg: float
  dose_per_kg: float
  frequency: str
  duration_days: Optional[int] = None
  max_dose_mg: Optional[float] = None
  formulation: Optional[str] = None
  notes: Optional[str] = None
  weight_kg: float
  is_max_capped: bool = False


class MedicationInfo(BaseModel):
  """Medication dosing information."""
  name: str
  dose_per_kg: float  # mg/kg/dose
  frequency: str
  max_single_dose: Optional[float] = None  # mg
  max_daily_dose: Optional[float] = None  # mg
  duration_days: Optional[int] = None
  formulations: list[str] = Field(default_factory=list)
  notes: Optional[str] = None


# Pediatric medication dosing database
# Source: AAP Red Book, Harriet Lane, Lexicomp
MEDICATIONS: dict[str, dict[str, MedicationInfo]] = {
  # Antibiotics
  "amoxicillin": {
    "aom_standard": MedicationInfo(
      name="Amoxicillin",
      dose_per_kg=40,  # mg/kg/day divided BID
      frequency="BID",
      max_single_dose=1500,
      duration_days=10,
      formulations=["125mg/5mL", "250mg/5mL", "400mg/5mL"],
      notes="Standard dose for uncomplicated AOM",
    ),
    "aom_high_dose": MedicationInfo(
      name="Amoxicillin",
      dose_per_kg=45,  # mg/kg/dose BID = 90mg/kg/day
      frequency="BID",
      max_single_dose=1500,
      duration_days=10,
      formulations=["400mg/5mL"],
      notes="High dose for resistant organisms or treatment failure",
    ),
    "strep_pharyngitis": MedicationInfo(
      name="Amoxicillin",
      dose_per_kg=25,  # mg/kg/dose BID
      frequency="BID",
      max_single_dose=500,
      duration_days=10,
      formulations=["250mg/5mL", "400mg/5mL"],
      notes="Alternative to penicillin V for strep throat",
    ),
    "sinusitis": MedicationInfo(
      name="Amoxicillin",
      dose_per_kg=45,
      frequency="BID",
      max_single_dose=1500,
      duration_days=10,
      formulations=["400mg/5mL"],
      notes="High dose for acute bacterial sinusitis",
    ),
    "cap_outpatient": MedicationInfo(
      name="Amoxicillin",
      dose_per_kg=45,
      frequency="BID",
      max_single_dose=1000,
      duration_days=5,
      formulations=["400mg/5mL"],
      notes="First-line for outpatient CAP in children",
    ),
  },
  "amoxicillin_clavulanate": {
    "aom_resistant": MedicationInfo(
      name="Amoxicillin-Clavulanate",
      dose_per_kg=45,  # based on amoxicillin component
      frequency="BID",
      max_single_dose=875,
      duration_days=10,
      formulations=["200-28.5mg/5mL", "400-57mg/5mL", "600-42.9mg/5mL ES"],
      notes="Use high-dose ES formulation. For treatment failure or beta-lactamase producers.",
    ),
    "sinusitis": MedicationInfo(
      name="Amoxicillin-Clavulanate",
      dose_per_kg=45,
      frequency="BID",
      max_single_dose=875,
      duration_days=10,
      formulations=["600-42.9mg/5mL ES"],
      notes="Second-line for sinusitis after amoxicillin failure",
    ),
    "uti": MedicationInfo(
      name="Amoxicillin-Clavulanate",
      dose_per_kg=12.5,  # per dose TID
      frequency="TID",
      max_single_dose=500,
      duration_days=7,
      formulations=["200-28.5mg/5mL", "400-57mg/5mL"],
      notes="Alternative for UTI based on culture sensitivities",
    ),
  },
  "azithromycin": {
    "cap": MedicationInfo(
      name="Azithromycin",
      dose_per_kg=10,  # Day 1, then 5mg/kg days 2-5
      frequency="Daily",
      max_single_dose=500,
      duration_days=5,
      formulations=["100mg/5mL", "200mg/5mL"],
      notes="10mg/kg day 1 (max 500mg), then 5mg/kg days 2-5 (max 250mg)",
    ),
    "pertussis": MedicationInfo(
      name="Azithromycin",
      dose_per_kg=10,
      frequency="Daily",
      max_single_dose=500,
      duration_days=5,
      formulations=["100mg/5mL", "200mg/5mL"],
      notes="Treatment and prophylaxis for pertussis",
    ),
  },
  "cephalexin": {
    "skin_soft_tissue": MedicationInfo(
      name="Cephalexin",
      dose_per_kg=12.5,  # per dose QID or 25 BID
      frequency="QID",
      max_single_dose=500,
      duration_days=7,
      formulations=["125mg/5mL", "250mg/5mL"],
      notes="First-line for uncomplicated cellulitis, impetigo",
    ),
    "uti": MedicationInfo(
      name="Cephalexin",
      dose_per_kg=12.5,
      frequency="QID",
      max_single_dose=500,
      duration_days=7,
      formulations=["125mg/5mL", "250mg/5mL"],
      notes="Alternative for UTI, check sensitivities",
    ),
  },
  "cefdinir": {
    "aom": MedicationInfo(
      name="Cefdinir",
      dose_per_kg=7,  # mg/kg/dose BID or 14 daily
      frequency="BID",
      max_single_dose=300,
      duration_days=10,
      formulations=["125mg/5mL", "250mg/5mL"],
      notes="Alternative for penicillin allergy (non-anaphylactic)",
    ),
    "sinusitis": MedicationInfo(
      name="Cefdinir",
      dose_per_kg=7,
      frequency="BID",
      max_single_dose=300,
      duration_days=10,
      formulations=["125mg/5mL", "250mg/5mL"],
      notes="Alternative for sinusitis with PCN allergy",
    ),
  },
  # Antivirals
  "oseltamivir": {
    "influenza_treatment": MedicationInfo(
      name="Oseltamivir (Tamiflu)",
      dose_per_kg=3,  # Simplified; actual is weight-banded
      frequency="BID",
      max_single_dose=75,
      duration_days=5,
      formulations=["6mg/mL suspension", "30mg capsule", "45mg capsule", "75mg capsule"],
      notes="Weight-based: <15kg: 30mg BID, 15-23kg: 45mg BID, 23-40kg: 60mg BID, >40kg: 75mg BID",
    ),
  },
  # Antipyretics/Analgesics
  "acetaminophen": {
    "fever_pain": MedicationInfo(
      name="Acetaminophen",
      dose_per_kg=15,  # mg/kg/dose
      frequency="Q4-6H PRN",
      max_single_dose=1000,
      max_daily_dose=75,  # mg/kg/day, max 4000mg/day
      formulations=["160mg/5mL", "325mg tablet", "500mg tablet"],
      notes="Max 5 doses/day. Do not exceed 75mg/kg/day or 4g/day.",
    ),
  },
  "ibuprofen": {
    "fever_pain": MedicationInfo(
      name="Ibuprofen",
      dose_per_kg=10,  # mg/kg/dose
      frequency="Q6-8H PRN",
      max_single_dose=400,
      max_daily_dose=40,  # mg/kg/day, max 1200mg/day
      formulations=["100mg/5mL", "200mg tablet"],
      notes="For children ≥6 months. Max 40mg/kg/day or 1200mg/day.",
    ),
  },
  # Steroids
  "prednisolone": {
    "asthma_exacerbation": MedicationInfo(
      name="Prednisolone",
      dose_per_kg=1,  # mg/kg/dose, often given as 2mg/kg/day divided BID
      frequency="Daily or BID",
      max_single_dose=60,
      duration_days=5,
      formulations=["15mg/5mL", "5mg/5mL"],
      notes="1-2mg/kg/day for 3-5 days. No taper needed for short courses.",
    ),
    "croup": MedicationInfo(
      name="Prednisolone",
      dose_per_kg=1,
      frequency="Single dose",
      max_single_dose=60,
      duration_days=1,
      formulations=["15mg/5mL"],
      notes="Single dose for croup. Dexamethasone often preferred.",
    ),
  },
  "dexamethasone": {
    "croup": MedicationInfo(
      name="Dexamethasone",
      dose_per_kg=0.6,  # mg/kg single dose
      frequency="Single dose",
      max_single_dose=10,
      duration_days=1,
      formulations=["0.5mg/5mL", "1mg/mL"],
      notes="Single dose. May repeat once in 24h if needed.",
    ),
    "asthma_exacerbation": MedicationInfo(
      name="Dexamethasone",
      dose_per_kg=0.6,
      frequency="Daily",
      max_single_dose=16,
      duration_days=2,
      formulations=["0.5mg/5mL", "1mg/mL"],
      notes="Alternative to pred burst. 1-2 doses may be as effective as 5-day pred.",
    ),
  },
  # GI Medications
  "ondansetron": {
    "nausea_vomiting": MedicationInfo(
      name="Ondansetron (Zofran)",
      dose_per_kg=0.15,  # mg/kg/dose
      frequency="Q8H PRN",
      max_single_dose=8,
      formulations=["4mg/5mL", "4mg ODT", "8mg ODT"],
      notes="Weight-based: 8-15kg: 2mg, 15-30kg: 4mg, >30kg: 8mg. Max 3 doses/day.",
    ),
  },
  # Allergy Medications
  "diphenhydramine": {
    "allergic_reaction": MedicationInfo(
      name="Diphenhydramine (Benadryl)",
      dose_per_kg=1.25,  # mg/kg/dose
      frequency="Q6H PRN",
      max_single_dose=50,
      formulations=["12.5mg/5mL"],
      notes="Causes sedation. For children ≥2 years.",
    ),
  },
  "cetirizine": {
    "allergic_rhinitis": MedicationInfo(
      name="Cetirizine (Zyrtec)",
      dose_per_kg=0,  # Age-based, not weight-based
      frequency="Daily",
      formulations=["5mg/5mL", "5mg chewable", "10mg tablet"],
      notes="Age-based: 6mo-2yr: 2.5mg, 2-6yr: 2.5-5mg, ≥6yr: 5-10mg daily",
    ),
  },
}


class DosingCalculator:
  """Calculate weight-based medication doses."""

  def __init__(self):
    self.medications = MEDICATIONS

  def calculate(
    self,
    medication: str,
    indication: str,
    weight_kg: float,
    age_months: Optional[int] = None,
  ) -> Optional[DoseResult]:
    """
    Calculate dose for a medication.

    Args:
      medication: Medication name (lowercase, underscored)
      indication: Indication key (e.g., "aom_standard", "fever_pain")
      weight_kg: Patient weight in kg
      age_months: Patient age in months (for age-specific dosing)

    Returns:
      DoseResult with calculated dose, or None if medication/indication not found
    """
    med_info = self.medications.get(medication, {}).get(indication)
    if not med_info:
      return None

    # Calculate base dose
    dose_mg = weight_kg * med_info.dose_per_kg

    # Apply max cap if present
    is_capped = False
    if med_info.max_single_dose and dose_mg > med_info.max_single_dose:
      dose_mg = med_info.max_single_dose
      is_capped = True

    return DoseResult(
      medication=med_info.name,
      indication=indication.replace("_", " ").title(),
      dose_mg=round(dose_mg, 1),
      dose_per_kg=med_info.dose_per_kg,
      frequency=med_info.frequency,
      duration_days=med_info.duration_days,
      max_dose_mg=med_info.max_single_dose,
      formulation=med_info.formulations[0] if med_info.formulations else None,
      notes=med_info.notes,
      weight_kg=weight_kg,
      is_max_capped=is_capped,
    )

  def get_all_formulations(self, medication: str, indication: str) -> list[str]:
    """Get all available formulations for a medication."""
    med_info = self.medications.get(medication, {}).get(indication)
    return med_info.formulations if med_info else []

  def list_medications(self) -> list[str]:
    """List all available medications."""
    return list(self.medications.keys())

  def list_indications(self, medication: str) -> list[str]:
    """List all indications for a medication."""
    return list(self.medications.get(medication, {}).keys())

  def validate_dose(
    self,
    medication: str,
    indication: str,
    proposed_dose_mg: float,
    weight_kg: float,
    tolerance_percent: float = 10,
  ) -> dict:
    """
    Validate a proposed dose against calculated dose.

    Returns dict with:
      - valid: bool
      - calculated_dose: float
      - difference_percent: float
      - message: str
    """
    calculated = self.calculate(medication, indication, weight_kg)
    if not calculated:
      return {
        "valid": False,
        "calculated_dose": None,
        "difference_percent": None,
        "message": f"Unknown medication/indication: {medication}/{indication}",
      }

    diff_percent = abs(proposed_dose_mg - calculated.dose_mg) / calculated.dose_mg * 100

    if diff_percent <= tolerance_percent:
      return {
        "valid": True,
        "calculated_dose": calculated.dose_mg,
        "difference_percent": round(diff_percent, 1),
        "message": "Dose is within acceptable range",
      }
    elif proposed_dose_mg > calculated.dose_mg:
      return {
        "valid": False,
        "calculated_dose": calculated.dose_mg,
        "difference_percent": round(diff_percent, 1),
        "message": f"Proposed dose ({proposed_dose_mg}mg) is higher than recommended ({calculated.dose_mg}mg)",
      }
    else:
      return {
        "valid": False,
        "calculated_dose": calculated.dose_mg,
        "difference_percent": round(diff_percent, 1),
        "message": f"Proposed dose ({proposed_dose_mg}mg) is lower than recommended ({calculated.dose_mg}mg)",
      }
