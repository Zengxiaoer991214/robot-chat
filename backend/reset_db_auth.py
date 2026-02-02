import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from app.core.database import engine, Base
from app.models import *  # Import all models to register them

def reset_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete.")

if __name__ == "__main__":
    reset_db()