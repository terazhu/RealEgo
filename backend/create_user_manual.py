import sys
import os
import logging

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import crud, schemas, auth

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("ManualUserCreate")

def create_manual_user():
    db = SessionLocal()
    username = "tera"
    password = "tera"
    
    try:
        logger.info(f"Checking if user '{username}' exists...")
        user = crud.get_user_by_username(db, username)
        
        if user:
            logger.info(f"User '{username}' already exists (ID: {user.id}). Updating password...")
            hashed_password = auth.get_password_hash(password)
            user.hashed_password = hashed_password
            db.commit()
            logger.info("Password updated successfully.")
        else:
            logger.info(f"User '{username}' does not exist. Creating...")
            user_in = schemas.UserCreate(username=username, password=password)
            new_user = crud.create_user(db, user_in)
            logger.info(f"User '{username}' created successfully (ID: {new_user.id}).")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    create_manual_user()
