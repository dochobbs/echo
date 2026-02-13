"""Test well-child patient generator."""

from src.cases.well_child_generator import WellChildGenerator


def test_generator_loads_well_child_frameworks():
  """Generator loads only well-child frameworks."""
  gen = WellChildGenerator()
  ages = gen.list_visit_ages()
  assert len(ages) == 13
  assert any(a["visit_age_months"] == 2 for a in ages)
  assert any(a["visit_age_months"] == 0 for a in ages)  # newborn


def test_generator_list_visit_ages_has_required_fields():
  """Each visit age entry has topic, visit_age_months, key."""
  gen = WellChildGenerator()
  for age in gen.list_visit_ages():
    assert "key" in age
    assert "topic" in age
    assert "visit_age_months" in age


def test_generator_get_framework():
  """Can retrieve a specific well-child framework."""
  gen = WellChildGenerator()
  fw = gen.get_framework("well_child_2mo")
  assert fw is not None
  assert fw.get("visit_age_months") == 2
  assert "immunizations_due" in fw
  assert "expected_milestones" in fw


def test_generator_get_framework_by_age():
  """Can retrieve framework by visit age."""
  gen = WellChildGenerator()
  result = gen.get_framework_by_age(12)
  assert result is not None
  key, fw = result
  assert key == "well_child_12mo"
  assert fw.get("visit_age_months") == 12


def test_generator_get_framework_by_age_not_found():
  """Returns None for invalid visit age."""
  gen = WellChildGenerator()
  result = gen.get_framework_by_age(7)
  assert result is None
