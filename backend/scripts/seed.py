"""
Phase 02 Seed & Schema Script

This script:
1. Connects to Supabase using the service role key (bypasses RLS)
2. Seeds the test data (firm, client, CMA project)
3. Can be re-run safely (checks for existing data)

Usage: python backend/scripts/seed.py
Or via the /admin/run-schema endpoint of the running FastAPI server
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv(backend_dir / ".env")

from app.db.supabase_client import get_supabase

def seed():
    db = get_supabase()
    print("Connected to Supabase")
    
    # ── Seed test firm ────────────────────────────────────────
    TEST_FIRM_EMAIL = "test@ashutosh-ca-firm.com"
    
    existing = db.table("firms").select("id").eq("email", TEST_FIRM_EMAIL).execute()
    if existing.data:
        firm_id = existing.data[0]["id"]
        print(f"✓ Test firm already exists: {firm_id}")
    else:
        result = db.table("firms").insert({
            "name": "Ashutosh CA Firm",
            "email": TEST_FIRM_EMAIL,
            "plan": "free",
        }).execute()
        firm_id = result.data[0]["id"]
        print(f"✓ Created test firm: {firm_id}")
    
    # ── Seed test client ────────────────────────────────────────
    existing = db.table("clients").select("id").eq("firm_id", firm_id).eq("name", "Mehta Computers").execute()
    if existing.data:
        client_id = existing.data[0]["id"]
        print(f"✓ Test client already exists: {client_id}")
    else:
        result = db.table("clients").insert({
            "firm_id": firm_id,
            "name": "Mehta Computers",
            "entity_type": "trading",
        }).execute()
        client_id = result.data[0]["id"]
        print(f"✓ Created test client: {client_id}")
    
    # ── Seed test CMA project ────────────────────────────────────────
    existing = db.table("cma_projects").select("id").eq("client_id", client_id).eq("financial_year", "2024-25").execute()
    if existing.data:
        project_id = existing.data[0]["id"]
        print(f"✓ Test CMA project already exists: {project_id}")
    else:
        result = db.table("cma_projects").insert({
            "firm_id": firm_id,
            "client_id": client_id,
            "financial_year": "2024-25",
            "bank_name": "State Bank of India",
            "loan_type": "working_capital",
            "status": "draft",
        }).execute()
        project_id = result.data[0]["id"]
        print(f"✓ Created test CMA project: {project_id}")
    
    print("\n✅ Seed complete!")
    print(f"  Firm ID:    {firm_id}")
    print(f"  Client ID:  {client_id}")
    print(f"  Project ID: {project_id}")
    return {"firm_id": firm_id, "client_id": client_id, "project_id": project_id}


if __name__ == "__main__":
    seed()
