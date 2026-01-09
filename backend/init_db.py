import sys
import os
import pymysql
from sqlalchemy import text, create_engine
from config import settings

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def init_db():
    print("Starting database initialization...")
    
    # 1. Create Database if it doesn't exist (using pymysql for raw connection)
    try:
        print(f"Connecting to MySQL host: {settings.MYSQL_HOST}...")
        conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        print(f"Checking database '{settings.MYSQL_DB}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f"Database '{settings.MYSQL_DB}' checked/created.")
        conn.close()
    except Exception as e:
        print(f"Error connecting/creating database: {e}")
        return

    # 2. Update Schema (Tables & Columns) using SQLAlchemy
    try:
        from database import engine, Base
        import models # Import models to register them
        
        print("Connecting to database via SQLAlchemy...")
        with engine.connect() as conn:
            
            # A. Check and update existing tables (e.g., profiles)
            print("Checking 'profiles' table schema...")
            try:
                # Check if 'profiles' table exists first to avoid error on select
                # But easiest way is to try select. If table doesn't exist, we skip to create_all
                conn.execute(text("SELECT 1 FROM profiles LIMIT 1"))
                
                # If table exists, check for columns
                # Check for history_limit
                try:
                    conn.execute(text("SELECT history_limit FROM profiles LIMIT 1"))
                    print("'history_limit' column already exists.")
                except Exception:
                    print("'history_limit' column missing. Adding it...")
                    conn.execute(text("ALTER TABLE profiles ADD COLUMN history_limit INT DEFAULT 100"))
                    print("Added 'history_limit' column to 'profiles' table.")
                
                # Check for timeline_data
                try:
                    conn.execute(text("SELECT timeline_data FROM profiles LIMIT 1"))
                    print("'timeline_data' column already exists.")
                except Exception:
                    print("'timeline_data' column missing. Adding it...")
                    conn.execute(text("ALTER TABLE profiles ADD COLUMN timeline_data TEXT"))
                    print("Added 'timeline_data' column to 'profiles' table.")
            except Exception:
                print("'profiles' table does not exist yet. Will be created.")

            # B. Create all missing tables (including chat_messages and profiles if missing)
            print("Creating missing tables...")
            Base.metadata.create_all(bind=engine)
            print("All tables checked/created.")
            
            print("Database initialization completed successfully.")
            
    except Exception as e:
        print(f"Error updating schema: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    init_db()
