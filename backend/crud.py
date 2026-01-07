from sqlalchemy.orm import Session
import models, schemas, auth

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Create empty profile
    db_profile = models.Profile(user_id=db_user.id)
    db.add(db_profile)
    db.commit()
    return db_user

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
