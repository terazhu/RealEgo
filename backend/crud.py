from sqlalchemy.orm import Session
import models, schemas, auth
import logging

logger = logging.getLogger("RealEgo")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    try:
        user = db.query(models.User).filter(models.User.username == username).first()
        if user:
            logger.debug(f"Found user in DB: {username}, ID: {user.id}")
        else:
            logger.debug(f"User not found in DB: {username}")
        return user
    except Exception as e:
        logger.error(f"Database error querying user {username}: {e}")
        return None

def create_user(db: Session, user: schemas.UserCreate):
    logger.debug(f"Attempting to create user: {user.username}")
    try:
        hashed_password = auth.get_password_hash(user.password)
        db_user = models.User(username=user.username, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        # Create empty profile
        db_profile = models.Profile(user_id=db_user.id)
        db.add(db_profile)
        db.commit()
        logger.debug(f"User created successfully: {user.username}, ID: {db_user.id}")
        return db_user
    except Exception as e:
        logger.error(f"Error creating user {user.username}: {e}")
        db.rollback()
        raise e

def get_profile(db: Session, user_id: int):
    return db.query(models.Profile).filter(models.Profile.user_id == user_id).first()

def update_profile(db: Session, user_id: int, profile: schemas.ProfileUpdate):
    db_profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if not db_profile:
        db_profile = models.Profile(user_id=user_id)
        db.add(db_profile)
    
    profile_data = profile.dict(exclude_unset=True)
    for key, value in profile_data.items():
        setattr(db_profile, key, value)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile

def create_chat_message(db: Session, user_id: int, role: str, content: str):
    try:
        db_msg = models.ChatMessage(user_id=user_id, role=role, content=content)
        db.add(db_msg)
        db.commit()
        db.refresh(db_msg)
        return db_msg
    except Exception as e:
        logger.error(f"Error creating chat message: {e}")
        db.rollback()
        return None

def get_chat_history(db: Session, user_id: int, limit: int = 100):
    try:
        # Get last N messages, ordered by timestamp desc, then reversed to show in chronological order
        messages = db.query(models.ChatMessage)\
            .filter(models.ChatMessage.user_id == user_id)\
            .order_by(models.ChatMessage.timestamp.desc())\
            .limit(limit)\
            .all()
        return list(reversed(messages))
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        return []
