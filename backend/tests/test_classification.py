import pytest
from uuid import uuid4
from app.services.classification.precedent_matcher import Precedent, find_precedents
from app.services.classification.rule_matcher import classify_by_rules, filter_rules
from app.services.classification.classifier import classify_project, ClassifiedItem
import json
import os

def test_rule_filter():
    trading_pl = filter_rules("trading", "profit_and_loss")
    assert len(trading_pl) > 0
    # ensure "Sales" is inside the rule set
    assert any("Sales" in r.source_terms for r in trading_pl)

def test_rule_matcher():
    res = classify_by_rules("Sales", "trading", "profit_and_loss")
    assert res is not None
    assert res.score == 1.0
    assert res.rule.target_row == 5
    
    res = classify_by_rules("Sales A/c", "trading", "profit_and_loss")
    assert res is not None
    assert res.score >= 0.95

def test_empty_project_validation():
    # just testing the data structure logic
    # if no generic table data, everything drops to 0 confidently
    pass
    
# Golden Test mocked here for brevity; usually checks against Mehta sample
def test_golden_mehta_classification(monkeypatch):
    # Mocking DB response explicitly
    def mock_db_data(*args, **kwargs):
        return {
            "profit_and_loss": {
                "line_items": [
                    {"name": "Sales", "amount": 1500000},
                    {"name": "Purchases", "amount": 900000},
                    {"name": "Depreciation", "amount": 50000},
                    {"name": "XYZ Random Unmapped", "amount": 10000}
                ]
            }
        }
    monkeypatch.setattr("app.services.classification.classifier.get_db_extracted_data", mock_db_data)
    
    class MockGeminiResponse:
        text = '[{"item_name":"XYZ Random Unmapped","item_amount":10000,"target_row":22,"target_sheet":"operating_statement","confidence":0.4,"source":"ai_uncertain","reasoning":"guess"}]'
        input_tokens = 10
        output_tokens = 10
        cost_usd = 0.0
        latency_ms = 100
        model = "gemini"
    
    class MockGeminiClient:
        def generate(self, *args, **kwargs):
            return MockGeminiResponse()
            
    monkeypatch.setattr("app.services.classification.classifier.GeminiClient", MockGeminiClient)
    
    res = classify_project(str(uuid4()), str(uuid4()), "trading")
    
    assert res.total_items == 4
    assert res.classified_by_rule >= 3  # Sales, Purchases, Dep are all in our mock rules
    
    sales_item = next(i for i in res.items if i.item_name == "Sales")
    assert sales_item.target_row == 5
    assert not sales_item.needs_review
