import os
import psycopg2
from dotenv import load_dotenv
import sys

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
PROJECT_REF = SUPABASE_URL.replace("https://", "").split(".")[0]

conn_str = f"postgresql://postgres.{PROJECT_REF}:{SERVICE_ROLE_KEY}@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require"

try:
    conn = psycopg2.connect(conn_str)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("ALTER TABLE cma_projects DROP CONSTRAINT cma_projects_status_check;")
    cur.execute("ALTER TABLE cma_projects ADD CONSTRAINT cma_projects_status_check CHECK (status IN ('draft', 'extracting', 'extracted', 'classifying', 'reviewing', 'validating', 'generating', 'completed', 'error'));")
    print("Added 'extracted' to cma_projects status.")
except Exception as e:
    print(f"Error: {e}")
