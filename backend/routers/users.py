from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas, crud, database, auth, models

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=schemas.User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@router.get("/me/profile", response_model=schemas.Profile)
async def read_own_profile(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    profile = crud.get_profile(db, user_id=current_user.id)
    if not profile:
        # Create default if missing (should be created at register)
        profile = models.Profile(user_id=current_user.id)
        db.add(profile)
        db.commit()
    return profile

@router.put("/me/profile", response_model=schemas.Profile)
async def update_own_profile(profile: schemas.ProfileUpdate, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    # Also sync to Mem0 logic here could be added
    # For now just DB update
    return crud.update_profile(db, user_id=current_user.id, profile=profile)
