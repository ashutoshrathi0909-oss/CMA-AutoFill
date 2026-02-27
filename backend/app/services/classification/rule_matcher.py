import re
from typing import List, Optional
from difflib import SequenceMatcher
from pydantic import BaseModel
from app.services.classification.rules_loader import get_all_rules, ClassificationRule

class RuleMatch(BaseModel):
    rule: ClassificationRule
    score: float
    matched_term: str
    match_type: str

def normalize_indian_term(term: str) -> str:
    term = term.lower().strip()
    
    # Remove A/c
    term = re.sub(r'\s*a/c\s*$', '', term)
    term = re.sub(r'\s*account\s*$', '', term)
    
    # Common prefixes
    term = re.sub(r'^s\.\s*debtors', 'sundry debtors', term)
    term = re.sub(r'^s\.\s*creditors', 'sundry creditors', term)
    term = re.sub(r'^dep\.', 'depreciation', term)
    term = re.sub(r'^prov\.', 'provision', term)
    term = re.sub(r'^misc\.', 'miscellaneous', term)
    
    # Clean multiple spaces
    term = re.sub(r'\s+', ' ', term)
    return term

def fuzzy_score(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def filter_rules(entity_type: str, document_type: str) -> List[ClassificationRule]:
    all_rules = get_all_rules()
    filtered = []
    
    for rule in all_rules:
        # Check entity
        if entity_type in rule.entity_types or not rule.entity_types:
            # Check document
            if document_type in rule.document_types or not rule.document_types:
                filtered.append(rule)
                
    return filtered

def match_item_to_rules(item_name: str, rules: List[ClassificationRule]) -> List[RuleMatch]:
    raw_name = item_name.strip()
    norm_name = normalize_indian_term(raw_name)
    
    matches = []
    
    for rule in rules:
        best_score = 0.0
        best_match_term = ""
        best_match_type = ""
        
        for term in rule.source_terms:
            raw_term = term.strip()
            norm_term = normalize_indian_term(raw_term)
            
            score = 0.0
            match_type = ""
            
            # Exact
            if raw_name.lower() == raw_term.lower():
                score = 1.0
                match_type = "exact"
            # Normalized
            elif norm_name == norm_term:
                if score < 0.95:
                    score = 0.95
                    match_type = "normalized"
            # Contains
            elif norm_term in norm_name or norm_name in norm_term:
                if len(norm_name) > 3 and len(norm_term) > 3:
                    if score < 0.80:
                        score = 0.80
                        match_type = "contains"
            # Fuzzy
            else:
                f_score = fuzzy_score(norm_name, norm_term)
                if f_score > 0.60 and f_score > score:
                    score = f_score
                    match_type = "fuzzy"
                    
            if score > best_score:
                best_score = score
                best_match_term = term
                best_match_type = match_type
                
        if best_score >= 0.60:
            matches.append(RuleMatch(
                rule=rule,
                score=best_score,
                matched_term=best_match_term,
                match_type=best_match_type
            ))
            
    # Sort descending
    matches.sort(key=lambda x: x.score, reverse=True)
    return matches

def classify_by_rules(item_name: str, entity_type: str, document_type: str) -> Optional[RuleMatch]:
    filtered = filter_rules(entity_type, document_type)
    matches = match_item_to_rules(item_name, filtered)
    
    if matches:
        return matches[0]
    return None
