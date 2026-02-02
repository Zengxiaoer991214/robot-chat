import os
import sys
from sqlalchemy import create_engine, text, select, insert, inspect
from sqlalchemy.orm import Session

# Ensure we can import app modules
sys.path.append(os.getcwd())

from app.core.database import Base
from app.models import User, Agent, Room, Role, Message, room_roles, ChatSession, ChatSessionMessage

# Configurations
SOURCE_DB_URL = "sqlite:///dev.db"
TARGET_DB_URL = "postgresql://coinradar:coinradar1234@117.72.55.252:9801/ai_chat_db"

def migrate():
    print(f"Connecting to source: {SOURCE_DB_URL}")
    source_engine = create_engine(SOURCE_DB_URL)
    
    print(f"Connecting to target: {TARGET_DB_URL}")
    target_engine = create_engine(TARGET_DB_URL)

    # 1. Create tables in target
    print("Creating tables in target database...")
    # Drop all tables first to ensure clean state (Optional, but safer for 'export to new db')
    print("Dropping existing tables in target...")
    Base.metadata.drop_all(target_engine)
    Base.metadata.create_all(target_engine)

    # 2. Get tables in dependency order
    # SQLAlchemy sorted_tables handles dependency order
    tables = Base.metadata.sorted_tables
    
    with source_engine.connect() as src_conn, target_engine.connect() as dst_conn:
        for table in tables:
            print(f"Migrating table: {table.name}")
            
            # Read from source
            # We need to use the table object bound to source metadata or just use text if name matches
            # Since 'table' is from Base.metadata, it's generic.
            
            try:
                # Select all data
                rows = src_conn.execute(table.select()).fetchall()
                
                if not rows:
                    print(f"  No data in {table.name}, skipping.")
                    continue
                
                print(f"  Found {len(rows)} rows. Inserting...")
                
                # Convert rows to list of dicts
                data = [dict(row._mapping) for row in rows]
                
                # Insert into target
                # We use chunking just in case
                chunk_size = 1000
                for i in range(0, len(data), chunk_size):
                    chunk = data[i:i+chunk_size]
                    dst_conn.execute(table.insert(), chunk)
                
                dst_conn.commit()
                print(f"  Done migrating {table.name}.")
                
                # Reset Sequence for ID columns (Postgres specific)
                if 'id' in table.c:
                    print(f"  Resetting sequence for {table.name}...")
                    seq_reset_sql = text(f"SELECT setval(pg_get_serial_sequence('{table.name}', 'id'), coalesce(max(id), 0) + 1, false) FROM {table.name}")
                    dst_conn.execute(seq_reset_sql)
                    dst_conn.commit()
                    
            except Exception as e:
                print(f"Error migrating {table.name}: {e}")
                # Don't raise, try next table? Or stop? 
                # Better stop to avoid inconsistency
                raise e

    print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()
