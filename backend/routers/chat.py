from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
import schemas, auth, models, database, crud
from services.llm import llm_service
from services.mem0 import mem0_service
import logging

logger = logging.getLogger("RealEgo")

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=schemas.ChatResponse)
async def chat(request: schemas.ChatRequest, background_tasks: BackgroundTasks, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    logger.info(f"Received chat request from user {current_user.username}: {request.message}")
    
    # 1. Get user profile for context
    profile = crud.get_profile(db, current_user.id)
    profile_dict = {}
    if profile:
        profile_dict = {
            "username": current_user.username,
            "full_name": profile.full_name,
            "birth_date": str(profile.birth_date) if profile.birth_date else None,
            "location": profile.location,
            "family_info": profile.family_info
        }
    logger.info(f"Loaded profile for user {current_user.username}: {profile_dict}")
    
    # 2. Get response from LLM
    response_text = llm_service.chat(request.message, str(current_user.id), profile_dict)
    logger.info(f"LLM Response: {response_text}")
    
    # 3. Add interaction to memory in BACKGROUND
    logger.info(f"Queueing memory update in background for user {current_user.username}")
    background_tasks.add_task(mem0_service.add_memory, f"User: {request.message}\nAssistant: {response_text}", str(current_user.id))
    
    return {"response": response_text}
