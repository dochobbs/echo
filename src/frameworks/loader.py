"""Framework loader for pediatric teaching frameworks."""

import random
from pathlib import Path
from typing import Optional
import yaml


FRAMEWORKS: dict[str, dict] = {}
_loaded = False


def load_frameworks(reload: bool = False) -> dict[str, dict]:
    """Load all teaching frameworks into memory.
    
    Args:
        reload: Force reload even if already loaded
        
    Returns:
        Dictionary mapping framework keys to framework data
    """
    global FRAMEWORKS, _loaded
    
    if _loaded and not reload:
        return FRAMEWORKS
    
    FRAMEWORKS.clear()
    framework_dir = Path("knowledge/frameworks")
    
    if not framework_dir.exists():
        return FRAMEWORKS
    
    for file in framework_dir.glob("*.yaml"):
        if file.name.startswith("_"):
            continue
        try:
            with open(file) as f:
                data = yaml.safe_load(f)
                if data and isinstance(data, dict):
                    key = file.stem
                    FRAMEWORKS[key] = data
        except Exception:
            continue
    
    _loaded = True
    return FRAMEWORKS


def get_framework(key: str) -> Optional[dict]:
    """Get a specific framework by key.
    
    Args:
        key: The framework key (e.g., 'otitis_media')
        
    Returns:
        Framework data or None if not found
    """
    if not _loaded:
        load_frameworks()
    return FRAMEWORKS.get(key)


def find_framework(condition_name: str) -> Optional[dict]:
    """Find framework by topic name or alias.
    
    Args:
        condition_name: Condition name to search for
        
    Returns:
        Framework data or None if not found
    """
    if not _loaded:
        load_frameworks()
    
    condition_lower = condition_name.lower()
    
    for key, framework in FRAMEWORKS.items():
        if key == condition_lower.replace(" ", "_"):
            return framework
        
        if framework.get("topic", "").lower() == condition_lower:
            return framework
        
        aliases = [a.lower() for a in framework.get("aliases", [])]
        if condition_lower in aliases:
            return framework
    
    return None


def get_frameworks_by_category(category: str) -> list[dict]:
    """Get all frameworks in a category.
    
    Args:
        category: Category name (e.g., 'infectious', 'respiratory')
        
    Returns:
        List of frameworks in the category with their keys
    """
    if not _loaded:
        load_frameworks()
    
    return [
        {"key": k, **v}
        for k, v in FRAMEWORKS.items()
        if v.get("category") == category
    ]


def get_all_framework_keys() -> list[str]:
    """Get list of all available framework keys."""
    if not _loaded:
        load_frameworks()
    return list(FRAMEWORKS.keys())


def get_random_framework() -> tuple[str, dict]:
    """Get a random framework.
    
    Returns:
        Tuple of (key, framework_data)
    """
    if not _loaded:
        load_frameworks()
    
    if not FRAMEWORKS:
        return ("", {})
    
    key = random.choice(list(FRAMEWORKS.keys()))
    return (key, FRAMEWORKS[key])


def get_teaching_context(condition_key: str) -> dict:
    """Get teaching context for providing feedback during a case.
    
    Args:
        condition_key: The framework key
        
    Returns:
        Dictionary with goals, pearls, mistakes, and red_flags
    """
    framework = get_framework(condition_key)
    
    if not framework:
        return {
            "goals": [],
            "pearls": [],
            "mistakes": [],
            "red_flags": [],
        }
    
    return {
        "goals": framework.get("teaching_goals", []),
        "pearls": framework.get("clinical_pearls", []),
        "mistakes": framework.get("common_mistakes", []),
        "red_flags": framework.get("red_flags", []),
    }


def build_case_prompt(condition_key: str, learner_level: str = "student") -> str:
    """Build prompt for Claude to generate a case.
    
    Args:
        condition_key: The framework key
        learner_level: Level of the learner (student, resident, etc.)
        
    Returns:
        Formatted prompt string
    """
    framework = get_framework(condition_key)
    
    if not framework:
        return "Generate a general pediatric case."
    
    age_range = framework.get("age_range_months", [0, 216])
    parent_styles = framework.get("parent_styles", ["concerned"])
    
    return f"""
Generate a pediatric case for teaching {framework.get('topic', condition_key)}.

TEACHING GOALS (what learner should understand):
{yaml.dump(framework.get('teaching_goals', []), default_flow_style=False)}

COMMON MISTAKES TO ADDRESS:
{yaml.dump(framework.get('common_mistakes', []), default_flow_style=False)}

RED FLAGS (must be recognized):
{yaml.dump(framework.get('red_flags', []), default_flow_style=False)}

CLINICAL PEARLS (high-yield points):
{yaml.dump(framework.get('clinical_pearls', []), default_flow_style=False)}

KEY HISTORY QUESTIONS:
{yaml.dump(framework.get('key_history_questions', []), default_flow_style=False)}

KEY EXAM FINDINGS:
{yaml.dump(framework.get('key_exam_findings', []), default_flow_style=False)}

TREATMENT PRINCIPLES:
{yaml.dump(framework.get('treatment_principles', []), default_flow_style=False)}

LEARNER LEVEL: {learner_level}
AGE RANGE: {age_range[0]}-{age_range[1]} months

Generate a realistic patient presentation within this age range.
Include parent personality from: {parent_styles}
"""


load_frameworks()
