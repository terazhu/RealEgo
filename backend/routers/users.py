from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import schemas, crud, database, auth, models
import json
from services.llm import llm_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/me/profile/voice", response_model=schemas.Profile)
async def update_profile_voice(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    # Get current profile timeline
    profile = crud.get_profile(db, user_id=current_user.id)
    current_timeline = json.loads(profile.timeline_data) if profile.timeline_data else {}
    
    # Process audio
    # llm_service is now async
    text, json_str = await llm_service.process_voice_profile(file.file, current_timeline)
    
    if not text:
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {json_str}")
        
    try:
        new_data = json.loads(json_str)
        # Merge logic (simple top-level merge)
        current_timeline.update(new_data)
        
        # Save back
        updated_profile = crud.update_profile(db, current_user.id, schemas.ProfileUpdate(timeline_data=json.dumps(current_timeline)))
        return updated_profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse LLM output: {e}")

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
