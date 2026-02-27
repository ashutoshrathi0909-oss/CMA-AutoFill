import os
import json
from pydantic import BaseModel, Field
from typing import List

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

_cached_rules: List[ClassificationRule] = None

def _load_rules():
    global _cached_rules
    if _cached_rules is not None:
        return
        
    json_path = os.path.join(os.path.dirname(__file__), "classification_rules.json")
    
    if not os.path.exists(json_path):
        _cached_rules = []
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    # parse
    _cached_rules = [ClassificationRule(**rule) for rule in data.get("rules", [])]

def get_all_rules() -> List[ClassificationRule]:
    if _cached_rules is None:
        _load_rules()
    return _cached_rules

def get_rules_count() -> int:
    if _cached_rules is None:
        _load_rules()
    return len(_cached_rules)
