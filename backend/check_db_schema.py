import psycopg2
import os
from urllib.parse import urlparse

# Get DB URL from .env or hardcoded based on previous reads
# DATABASE_URL=postgresql://coinradar:coinradar1234@117.72.55.252:9801/ai_chat_db
DB_URL = "postgresql://coinradar:coinradar1234@117.72.55.252:9801/ai_chat_db"

def check_schema():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # Check columns in agents table
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'agents';
        """)
        
        columns = cur.fetchall()
        print("Columns in agents table:")
        found_api_key = False
        for col in columns:
            print(f"- {col[0]} ({col[1]})")
            if col[0] == 'api_key_config':
                found_api_key = True
                
        if not found_api_key:
            print("\nWARNING: api_key_config column is MISSING!")
            # Attempt to add it? 
            # Better to just report it first.
        else:
            print("\nSUCCESS: api_key_config column exists.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error connecting to DB: {e}")

if __name__ == "__main__":
    check_schema()
