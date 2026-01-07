from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, auth, models, database, crud
from services.llm import llm_service
from services.mem0 import mem0_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=schemas.ChatResponse)
async def chat(request: schemas.ChatRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
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
    
    # 2. Get response from LLM
    response_text = llm_service.chat(request.message, str(current_user.id), profile_dict)
    
    # 3. Add interaction to memory
    mem0_service.add_memory(f"User: {request.message}\nAssistant: {response_text}", str(current_user.id))
    
    return {"response": response_text}
