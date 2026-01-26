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
    print("Starting schema migration for Role-based architecture...")
    try:
        inspector = inspect(engine)
        
        # 1. Drop room_agents table if exists
        try:
            if inspector.has_table("room_agents"):
                print(" - 'room_agents' table found. Dropping it...")
                with engine.begin() as connection:
                    connection.execute(text("DROP TABLE room_agents CASCADE;"))
                print(" - Success: Dropped 'room_agents'.")
            else:
                print(" - 'room_agents' table not found. Skipping.")
        except Exception as e:
            print(f"Error dropping 'room_agents': {e}")

        # 2. Create room_roles table
        try:
            if not inspector.has_table("room_roles"):
                print(" - 'room_roles' table missing. Creating it...")
                with engine.begin() as connection:
                    connection.execute(text("""
                        CREATE TABLE room_roles (
                            room_id INTEGER NOT NULL,
                            role_id INTEGER NOT NULL,
                            PRIMARY KEY (room_id, role_id),
                            FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE,
                            FOREIGN KEY(role_id) REFERENCES roles(id) ON DELETE CASCADE
                        );
                    """))
                print(" - Success: Created 'room_roles'.")
            else:
                print(" - 'room_roles' table already exists. Skipping.")
        except Exception as e:
            print(f"Error creating 'room_roles': {e}")

        # 3. Update 'messages' table
        try:
            columns = [col['name'] for col in inspector.get_columns('messages')]
            if 'role_id' in columns:
                print(" - 'role_id' already exists in 'messages'. Skipping.")
            else:
                print(" - 'role_id' missing in 'messages'. Adding it...")
                with engine.begin() as connection:
                    connection.execute(text("ALTER TABLE messages ADD COLUMN role_id INTEGER REFERENCES roles(id);"))
                print(" - Success: Added 'role_id' to 'messages'.")
        except Exception as e:
             print(f"Error checking/updating 'messages': {e}")

        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    run_migration()
