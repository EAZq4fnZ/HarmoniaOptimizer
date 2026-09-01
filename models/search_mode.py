# models/search_mode.py

from __future__ import annotations

from enum import StrEnum


class SearchMode(StrEnum):
    FAST = "fast"
    STANDARD = "standard"
    DEEP = "deep"
