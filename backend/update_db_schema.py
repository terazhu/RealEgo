import sys
import os
from sqlalchemy import text
from database import engine

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def update_schema():
    print("Starting database schema update...")
    with engine.connect() as conn:
        try:
            # 1. Create chat_messages table if not exists
            # Note: SQLAlchemy's create_all usually handles this for new tables, 
            # but since we are running this manually, let's be explicit or rely on metadata.create_all
            # Actually, the best way for existing DB is to check and add columns/tables.
            
            # Since we added a new table 'chat_messages', we can try to create it.
            # But create_all in main.py only creates tables that don't exist.
            # So simply restarting the server (which calls create_all) will create the NEW table.
            
            # However, for EXISTING tables (like profiles), we need to ALTER them to add columns.
            
            print("Checking 'profiles' table for 'history_limit' column...")
            try:
                # Check if column exists (MySQL specific query, or just try to select it)
                conn.execute(text("SELECT history_limit FROM profiles LIMIT 1"))
                print("'history_limit' column already exists.")
            except Exception:
                print("'history_limit' column missing. Adding it...")
                conn.execute(text("ALTER TABLE profiles ADD COLUMN history_limit INT DEFAULT 100"))
                print("Added 'history_limit' column to 'profiles' table.")
                
            # For the new table 'chat_messages', we can trigger create_all
            from database import Base
            import models # Import models to register them
            Base.metadata.create_all(bind=engine)
            print("Checked/Created 'chat_messages' table.")
            
            print("Schema update completed successfully.")
            
        except Exception as e:
            print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
