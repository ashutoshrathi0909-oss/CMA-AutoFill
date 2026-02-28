import logging
import os
import json
from pydantic import BaseModel
from typing import List

logger = logging.getLogger(__name__)


class ClassificationRule(BaseModel):
    id: int
    source_terms: List[str]
    target_row: int
    target_sheet: str
    target_label: str
    entity_types: List[str]
    document_types: List[str]
    priority: int
    match_type: str
    notes: str = ""


_cached_rules: List[ClassificationRule] = []
_loaded: bool = False


def _load_rules() -> None:
    global _cached_rules, _loaded

    if _loaded:
        return

    json_path = os.path.join(os.path.dirname(__file__), "classification_rules.json")

    if not os.path.exists(json_path):
        logger.warning("Classification rules file not found at %s — using empty rules", json_path)
        _cached_rules = []
        _loaded = True
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _cached_rules = [ClassificationRule(**rule) for rule in data.get("rules", [])]
        logger.info("Loaded %d classification rules", len(_cached_rules))
    except Exception as e:
        logger.error("Failed to load classification rules: %s", e)
        _cached_rules = []

    _loaded = True


def get_all_rules() -> List[ClassificationRule]:
    if not _loaded:
        _load_rules()
    return _cached_rules


def get_rules_count() -> int:
    if not _loaded:
        _load_rules()
    return len(_cached_rules)
