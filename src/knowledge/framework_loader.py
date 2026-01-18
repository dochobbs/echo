"""
Framework Loader for Echo Teaching Frameworks

This module loads and provides access to the 100 pediatric condition
teaching frameworks used for dynamic case generation.
"""

import yaml
from pathlib import Path
from typing import Optional


class FrameworkLoader:
    """Load and query teaching frameworks."""

    def __init__(self, framework_dir: str = "knowledge/frameworks"):
        self.framework_dir = Path(framework_dir)
        self._frameworks: dict = {}
        self._by_category: dict = {}
        self._alias_map: dict = {}
        self._load_all()

    def _load_all(self):
        """Load all framework YAML files."""
        if not self.framework_dir.exists():
            raise FileNotFoundError(f"Framework directory not found: {self.framework_dir}")

        for file in self.framework_dir.glob("*.yaml"):
            if file.name.startswith("_"):
                continue

            try:
                with open(file, "r") as f:
                    data = yaml.safe_load(f)

                key = file.stem
                self._frameworks[key] = data

                # Index by category
                category = data.get("category", "other")
                if category not in self._by_category:
                    self._by_category[category] = []
                self._by_category[category].append(key)

                # Index aliases
                for alias in data.get("aliases", []):
                    self._alias_map[alias.lower()] = key

            except Exception as e:
                print(f"Warning: Failed to load {file}: {e}")

    def get(self, key: str) -> Optional[dict]:
        """Get framework by key (filename without .yaml)."""
        return self._frameworks.get(key)

    def find(self, name: str) -> Optional[dict]:
        """Find framework by topic name or alias."""
        name_lower = name.lower()

        # Try direct key match
        key = name_lower.replace(" ", "_").replace("-", "_")
        if key in self._frameworks:
            return self._frameworks[key]

        # Try alias match
        if name_lower in self._alias_map:
            return self._frameworks[self._alias_map[name_lower]]

        # Try topic name match
        for fw in self._frameworks.values():
            if fw.get("topic", "").lower() == name_lower:
                return fw

        return None

    def get_by_category(self, category: str) -> list[dict]:
        """Get all frameworks in a category."""
        keys = self._by_category.get(category, [])
        return [self._frameworks[k] for k in keys]

    def get_categories(self) -> list[str]:
        """Get list of all categories."""
        return list(self._by_category.keys())

    def get_all_keys(self) -> list[str]:
        """Get all framework keys."""
        return list(self._frameworks.keys())

    def get_random(self, category: str = None) -> tuple[str, dict]:
        """Get a random framework, optionally filtered by category."""
        import random

        if category:
            keys = self._by_category.get(category, [])
        else:
            keys = list(self._frameworks.keys())

        if not keys:
            raise ValueError(f"No frameworks found for category: {category}")

        key = random.choice(keys)
        return key, self._frameworks[key]

    def get_for_age(self, age_months: int) -> list[tuple[str, dict]]:
        """Get all frameworks appropriate for a given age."""
        results = []
        for key, fw in self._frameworks.items():
            age_range = fw.get("age_range_months", [0, 216])
            if age_range[0] <= age_months <= age_range[1]:
                results.append((key, fw))
        return results

    def summary(self) -> dict:
        """Get summary statistics."""
        return {
            "total_frameworks": len(self._frameworks),
            "categories": {
                cat: len(keys) for cat, keys in self._by_category.items()
            },
            "total_aliases": len(self._alias_map),
        }

    def get_teaching_context(self, key: str) -> dict:
        """Get teaching context for a framework (for prompts)."""
        fw = self.get(key)
        if not fw:
            return {}

        # Filter images to only include those with valid URLs (not PLACEHOLDER)
        raw_images = fw.get("images", [])
        valid_images = [
            img for img in raw_images
            if img.get("url") and img.get("url") != "PLACEHOLDER"
        ]

        return {
            "topic": fw.get("topic"),
            "teaching_goals": fw.get("teaching_goals", []),
            "common_mistakes": fw.get("common_mistakes", []),
            "red_flags": fw.get("red_flags", []),
            "clinical_pearls": fw.get("clinical_pearls", []),
            "key_history_questions": fw.get("key_history_questions", []),
            "key_exam_findings": fw.get("key_exam_findings", []),
            "treatment_principles": fw.get("treatment_principles", []),
            "disposition_guidance": fw.get("disposition_guidance", []),
            "parent_styles": fw.get("parent_styles", []),
            "images": valid_images,
        }

    def build_case_prompt(self, key: str, learner_level: str = "student") -> str:
        """Build a case generation prompt using framework context."""
        fw = self.get(key)
        if not fw:
            return "Generate a general pediatric case."

        age_range = fw.get("age_range_months", [12, 120])
        parent_styles = fw.get("parent_styles", ["concerned"])

        prompt = f"""Generate a pediatric case for teaching {fw['topic']}.

## TEACHING GOALS (what the learner should understand)
{self._format_list(fw.get('teaching_goals', []))}

## COMMON LEARNER MISTAKES TO ADDRESS
{self._format_list(fw.get('common_mistakes', []))}

## RED FLAGS (safety-critical findings - must be recognized)
{self._format_list(fw.get('red_flags', []))}

## CLINICAL PEARLS (high-yield teaching points)
{self._format_list(fw.get('clinical_pearls', []))}

## KEY HISTORY QUESTIONS (learner should ask)
{self._format_list(fw.get('key_history_questions', []))}

## KEY EXAM FINDINGS (learner should look for)
{self._format_list(fw.get('key_exam_findings', []))}

## TREATMENT PRINCIPLES
{self._format_list(fw.get('treatment_principles', []))}

## CASE PARAMETERS
- Learner Level: {learner_level}
- Patient Age Range: {age_range[0]}-{age_range[1]} months
- Parent Personality Options: {', '.join(parent_styles)}

Generate a realistic patient presentation within these parameters. Create a specific parent character from the personality options. Make the case challenging but fair for the learner level.
"""
        return prompt

    def _format_list(self, items: list) -> str:
        """Format a list for prompt inclusion."""
        if not items:
            return "- None specified"
        return "\n".join(f"- {item}" for item in items)


# Singleton instance for easy import
_loader: Optional[FrameworkLoader] = None


def get_frameworks() -> FrameworkLoader:
    """Get the singleton FrameworkLoader instance."""
    global _loader
    if _loader is None:
        _loader = FrameworkLoader()
    return _loader


# Convenience functions
def get_framework(key: str) -> Optional[dict]:
    """Get a framework by key."""
    return get_frameworks().get(key)


def find_framework(name: str) -> Optional[dict]:
    """Find a framework by name or alias."""
    return get_frameworks().find(name)


def get_teaching_context(key: str) -> dict:
    """Get teaching context for a condition."""
    return get_frameworks().get_teaching_context(key)


def build_case_prompt(key: str, learner_level: str = "student") -> str:
    """Build a case generation prompt."""
    return get_frameworks().build_case_prompt(key, learner_level)
