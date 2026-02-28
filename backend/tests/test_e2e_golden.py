import pytest
import os
from uuid import uuid4
from app.services.classification.classifier import classify_project, ClassifiedItem
from app.services.excel.generator import generate_cma
from app.services.validation.validator import validate_project
from app.api.v1.endpoints.generation import GenerateRequest

# Creating a class to run our pseudo-Golden assertions.
class TestE2EGoldenMehta:
    def test_end_to_end_golden(self, monkeypatch):
        mock_proj_id = str(uuid4())
        mock_firm_id = str(uuid4())
        
        # 1. Mock DB data fetching extraction
        def mock_extracted_data(*args, **kwargs):
            return {
                "profit_and_loss": {
                    "line_items": [
                        {"name": "Sales", "amount": 1500000},
                        {"name": "Purchases", "amount": 900000}
                    ]
                }
            }
        monkeypatch.setattr("app.services.classification.classifier.get_db_extracted_data", mock_extracted_data)
        
        # Mock Gemini for classification
        class MockGeminiResponse:
            text = '[]'
            cost_usd = 0.0
            input_tokens = 0
            output_tokens = 0
        
        class MockGeminiClient:
            def generate(self, *args, **kwargs):
                return MockGeminiResponse()
                
        monkeypatch.setattr("app.services.classification.classifier.GeminiClient", MockGeminiClient)
        
        # 2. Mock Classifications to avoid full DB load
        # Wait, the classifier calls local rules natively.
        
        # Just calling the generator safely via mock setup might be brittle if Supabase fails inside it,
        # Let's mock DB instances.
        def mock_supabase_db(*args, **kwargs):
            class MockTable:
                def __init__(self, data):
                    self._data = data
                def select(self, *args, **kwargs): return self
                def eq(self, *args, **kwargs): return self
                def execute(self):
                    class Res:
                        data = self._data
                    return Res()
                def insert(self, *args, **kwargs): return self
                def update(self, *args, **kwargs): return self
                
            class MockStorage:
                class MockBucket:
                    def upload(self, *args, **kwargs): pass
                    def create_signed_url(self, *args, **kwargs): return {"signedURL": "mock_url"}
                def from_(self, bucket): return self.MockBucket()
                
            class DB:
                def table(self, name):
                    if name == "cma_projects":
                        return MockTable([{"id": mock_proj_id, "client_id": str(uuid4()), "status": "extracted", "classification_data": {"items": [{"item_name": "Sales", "target_row": 5, "target_sheet": "operating_statement", "item_amount": 1500000}]}}])
                    if name == "clients":
                        return MockTable([{"name": "Mehta Computers", "entity_type": "trading"}])
                    if name == "generated_files":
                        return MockTable([])
                    return MockTable([])
                storage = MockStorage()
            return DB()
            
        monkeypatch.setattr("app.services.excel.generator.get_supabase", mock_supabase_db)
        
        class MockWriter:
            def __init__(self, template_path):
                self.template_path = template_path
            def write(self, data, output_path):
                with open(output_path, "wb") as f:
                    f.write(b"mocked bytes")
                return output_path
        monkeypatch.setattr("app.services.excel.generator.CMAWriter", MockWriter)
        
        # 3. Generating!
        res = generate_cma(mock_proj_id, mock_firm_id, skip_validation=True)
        assert res is not None
        assert res.success is True
        assert res.file_size > 0
        assert "MehtaComputers" in res.file_name
