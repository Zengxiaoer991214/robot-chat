import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment.")
    exit(1)

print(f"Connecting to database: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)

def run_migration():
    print("Starting schema migration...")
    try:
        inspector = inspect(engine)
        
        # Check and update 'rooms' table
        try:
            columns = [col['name'] for col in inspector.get_columns('rooms')]
            if 'session_id' in columns:
                print(" - 'session_id' already exists in 'rooms'. Skipping.")
            else:
                print(" - 'session_id' missing in 'rooms'. Adding it...")
                with engine.begin() as connection:
                    connection.execute(text("ALTER TABLE rooms ADD COLUMN session_id INTEGER DEFAULT 0 NOT NULL;"))
                print(" - Success: Added 'session_id' to 'rooms'.")
        except Exception as e:
            print(f"Error checking/updating 'rooms': {e}")

        # Check and update 'messages' table
        try:
            columns = [col['name'] for col in inspector.get_columns('messages')]
            if 'session_id' in columns:
                print(" - 'session_id' already exists in 'messages'. Skipping.")
            else:
                print(" - 'session_id' missing in 'messages'. Adding it...")
                with engine.begin() as connection:
                    connection.execute(text("ALTER TABLE messages ADD COLUMN session_id INTEGER DEFAULT 0 NOT NULL;"))
                print(" - Success: Added 'session_id' to 'messages'.")
        except Exception as e:
             print(f"Error checking/updating 'messages': {e}")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    run_migration()
