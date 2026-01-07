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
