"""Teaching Frameworks module for Echo medical tutor.

Provides 100 pediatric condition teaching frameworks that guide AI tutoring.
"""

from .loader import (
    load_frameworks,
    get_framework,
    find_framework,
    get_frameworks_by_category,
    get_all_framework_keys,
    get_random_framework,
    get_teaching_context,
    FRAMEWORKS,
)

__all__ = [
    "load_frameworks",
    "get_framework",
    "find_framework",
    "get_frameworks_by_category",
    "get_all_framework_keys",
    "get_random_framework",
    "get_teaching_context",
    "FRAMEWORKS",
]
