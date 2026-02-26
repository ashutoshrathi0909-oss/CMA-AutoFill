"""
Execute Phase 02 SQL via psycopg2 using Supabase Transaction Pooler.
Connection: postgresql://postgres.[project_ref]:[service_role_key]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
PROJECT_REF = SUPABASE_URL.replace("https://", "").split(".")[0]

SQL_FILE = os.path.join(os.path.dirname(__file__), "phase02_schema.sql")
with open(SQL_FILE, "r", encoding="utf-8") as f:
    full_sql = f.read()

print(f"Project: {PROJECT_REF}")
print(f"SQL length: {len(full_sql)} chars")

# Supabase Transaction Pooler — uses service_role key as password
# User format: postgres.[project_ref]
POOLER_HOST = "aws-0-ap-south-1.pooler.supabase.com"
POOLER_PORT = 6543
DB_USER = f"postgres.{PROJECT_REF}"
DB_PASSWORD = SERVICE_ROLE_KEY  # service_role key works as password for pooler
DB_NAME = "postgres"

conn_str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{POOLER_HOST}:{POOLER_PORT}/{DB_NAME}?sslmode=require"

print(f"\nConnecting to: {POOLER_HOST}:{POOLER_PORT} as {DB_USER}")

try:
    conn = psycopg2.connect(conn_str)
    conn.autocommit = True
    cur = conn.cursor()
    
    print("Connected! Executing schema...")
    cur.execute(full_sql)
    
    print("\n✅ Schema executed successfully!")
    
    # Verify tables were created
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tables = [row[0] for row in cur.fetchall()]
    print(f"\nTables in public schema ({len(tables)}):")
    for t in tables:
        print(f"  ✓ {t}")
    
    cur.close()
    conn.close()

except psycopg2.OperationalError as e:
    print(f"Connection failed: {e}")
    print("\nNote: If this pooler host doesn't work, check your Supabase dashboard")
    print("Project Settings → Database → Connection string → Transaction pooler")
    sys.exit(1)
except psycopg2.Error as e:
    print(f"SQL error: {e}")
    sys.exit(1)
