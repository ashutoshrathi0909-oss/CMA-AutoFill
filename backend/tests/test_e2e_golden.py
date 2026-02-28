import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from app.services.excel.generator import generate_cma


class TestE2EGoldenMehta:
    def test_end_to_end_golden(self, monkeypatch):
        mock_proj_id = str(uuid4())
        mock_firm_id = str(uuid4())
        mock_client_id = str(uuid4())

        # Mock Supabase DB
        def mock_supabase_db():
            class MockTable:
                def __init__(self, data):
                    self._table_data = data

                def select(self, *args, **kwargs):
                    return self

                def eq(self, *args, **kwargs):
                    return self

                def neq(self, *args, **kwargs):
                    return self

                def execute(self):
                    res = MagicMock()
                    res.data = self._table_data
                    return res

                def insert(self, *args, **kwargs):
                    return self

                def update(self, *args, **kwargs):
                    return self

            class MockStorage:
                class MockBucket:
                    def upload(self, *args, **kwargs):
                        pass

                    def create_signed_url(self, *args, **kwargs):
                        return {"signedURL": "mock_url"}

                def from_(self, bucket):
                    return self.MockBucket()

            class DB:
                def table(self, name):
                    if name == "cma_projects":
                        return MockTable([{
                            "id": mock_proj_id,
                            "client_id": mock_client_id,
                            "financial_year": "2024-25",
                            "status": "extracted",
                            "classification_data": {
                                "items": [{
                                    "item_name": "Sales",
                                    "target_row": 5,
                                    "target_sheet": "operating_statement",
                                    "item_amount": 1500000,
                                }],
                            },
                        }])
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

        res = generate_cma(mock_proj_id, mock_firm_id, skip_validation=True)
        assert res is not None
        assert res.success is True
        assert res.file_size > 0
        assert "MehtaComputers" in res.file_name
        assert res.file_name.endswith(".xlsm")
        assert "2024-25" in res.file_name
