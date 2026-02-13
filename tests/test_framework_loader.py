"""Test framework loader with well-child support."""

from src.frameworks.loader import (
  load_frameworks, get_framework, get_frameworks_by_category,
  get_well_child_frameworks, get_well_child_by_age,
)


def test_load_includes_well_child():
  """Loader picks up well_child framework files."""
  frameworks = load_frameworks(reload=True)
  wc_keys = [k for k in frameworks if k.startswith("well_child_")]
  assert len(wc_keys) == 13


def test_get_well_child_frameworks():
  """get_well_child_frameworks returns only well-child frameworks."""
  wc = get_well_child_frameworks()
  assert len(wc) == 13
  for fw in wc:
    assert fw.get("category") == "well_child"


def test_get_well_child_by_age():
  """get_well_child_by_age returns correct framework."""
  fw = get_well_child_by_age(2)
  assert fw is not None
  assert fw.get("visit_age_months") == 2
  assert "teaching_goals" in fw


def test_get_well_child_by_age_not_found():
  """get_well_child_by_age returns None for invalid age."""
  fw = get_well_child_by_age(7)  # No 7-month well-child visit
  assert fw is None


def test_get_frameworks_by_category_well_child():
  """get_frameworks_by_category works for well_child."""
  wc = get_frameworks_by_category("well_child")
  assert len(wc) == 13
