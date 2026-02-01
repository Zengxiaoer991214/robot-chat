import sqlite3
import os

# Database path
DB_PATH = "dev.db"

def add_mode_column():
    if not os.path.exists(DB_PATH):
        print(f"Database file {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(rooms)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'mode' in columns:
            print("Column 'mode' already exists in 'rooms' table.")
        else:
            print("Adding 'mode' column to 'rooms' table...")
            # Add the column with a default value of 'debate'
            cursor.execute("ALTER TABLE rooms ADD COLUMN mode VARCHAR(20) DEFAULT 'debate' NOT NULL")
            conn.commit()
            print("Column 'mode' added successfully.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_mode_column()
