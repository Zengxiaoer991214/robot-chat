from sqlalchemy import create_engine, text, inspect
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL not found in .env")
    exit(1)

# Fix for SQLAlchemy 1.4+ compatibility with postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def run_migration():
    print("Starting schema migration for Roles...")
    try:
        inspector = inspect(engine)
        
        # 1. Create 'roles' table if not exists
        if not inspector.has_table("roles"):
            print(" - 'roles' table missing. Creating it...")
            with engine.begin() as connection:
                connection.execute(text("""
                    CREATE TABLE roles (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        gender VARCHAR(20),
                        age VARCHAR(20),
                        profession VARCHAR(100),
                        personality TEXT,
                        aggressiveness INTEGER DEFAULT 5 NOT NULL,
                        agent_id INTEGER NOT NULL REFERENCES agents(id),
                        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc') NOT NULL
                    );
                """))
                connection.execute(text("CREATE INDEX ix_roles_id ON roles (id);"))
            print(" - Success: Created 'roles' table.")
        else:
            print(" - 'roles' table already exists. Skipping.")

        # 2. Create 'room_roles' association table if not exists
        if not inspector.has_table("room_roles"):
            print(" - 'room_roles' table missing. Creating it...")
            with engine.begin() as connection:
                connection.execute(text("""
                    CREATE TABLE room_roles (
                        room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
                        role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
                        PRIMARY KEY (room_id, role_id)
                    );
                """))
            print(" - Success: Created 'room_roles' table.")
        else:
            print(" - 'room_roles' table already exists. Skipping.")

        # 3. Add 'mode' column to 'rooms' table
        columns = [col['name'] for col in inspector.get_columns('rooms')]
        if 'mode' in columns:
            print(" - 'mode' column already exists in 'rooms'. Skipping.")
        else:
            print(" - 'mode' column missing in 'rooms'. Adding it...")
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE rooms ADD COLUMN mode VARCHAR(20) DEFAULT 'debate' NOT NULL;"))
            print(" - Success: Added 'mode' to 'rooms'.")
            
        # 4. Add 'sender_name' column to 'messages' table
        columns = [col['name'] for col in inspector.get_columns('messages')]
        if 'sender_name' in columns:
            print(" - 'sender_name' column already exists in 'messages'. Skipping.")
        else:
            print(" - 'sender_name' column missing in 'messages'. Adding it...")
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE messages ADD COLUMN sender_name VARCHAR(100);"))
            print(" - Success: Added 'sender_name' to 'messages'.")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    run_migration()
