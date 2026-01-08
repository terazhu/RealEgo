from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import schemas, auth, models, database, crud
from services.llm import llm_service
from services.mem0 import mem0_service
import logging
import json
import asyncio

logger = logging.getLogger("RealEgo")

router = APIRouter(prefix="/chat", tags=["chat"])

from typing import List

@router.get("/history", response_model=List[schemas.ChatMessage])
async def get_history(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    profile = crud.get_profile(db, current_user.id)
    limit = 100
    if profile and profile.history_limit:
        limit = profile.history_limit
    
    logger.info(f"Fetching chat history for user {current_user.username} with limit {limit}")
    return crud.get_chat_history(db, current_user.id, limit)

@router.post("/", response_class=StreamingResponse)
async def chat(request: schemas.ChatRequest, background_tasks: BackgroundTasks, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    logger.info(f"Received chat request from user {current_user.username}: {request.message}")
    
    # Save user message (Background)
    background_tasks.add_task(crud.create_chat_message, db, current_user.id, "user", request.message)

    async def event_generator():
        try:
            # 1. Load Profile
            yield json.dumps({"type": "log", "content": "Loading user profile..."}) + "\n"
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
            yield json.dumps({"type": "log", "content": "Profile loaded."}) + "\n"

            # 2. Search Memory (Simulated separate step for visualization, though LLM service does it)
            # Actually, to show it properly, we should probably refactor LLM service to expose this, 
            # or just log it here as if we are doing it.
            # Let's peek into mem0 service manually to show the log, then pass to LLM service.
            # OR just fake the log sequence if it happens fast inside llm_service.
            # Ideally, we call mem0 search here explicitly.
            
            yield json.dumps({"type": "log", "content": "Searching relevant memories..."}) + "\n"
            # We can't easily split llm_service.chat without refactoring it heavily. 
            # For now, we will log it, and let llm_service do its job.
            # Or better: let's do the search here to show the count!
            memories = mem0_service.search_memory(request.message, str(current_user.id))
            mem_count = len(memories) if memories else 0
            yield json.dumps({"type": "log", "content": f"Found {mem_count} relevant memories."}) + "\n"

            # 3. Call LLM
            yield json.dumps({"type": "log", "content": "Constructing prompt and waiting for LLM..."}) + "\n"
            
            # Note: We are re-implementing part of llm_service.chat here to inject logs or just calling it.
            # If we call llm_service.chat, it does memory search AGAIN. That's wasteful.
            # Let's use a modified version or just accept the double search for now (mem0 is fast/cached usually).
            # ACTUALLY, let's just use llm_service.chat and assume the logs above are "pre-flight checks".
            
            response_text = llm_service.chat(request.message, str(current_user.id), profile_dict)
            
            yield json.dumps({"type": "log", "content": "LLM response received."}) + "\n"
            yield json.dumps({"type": "response", "content": response_text}) + "\n"
            
            # 4. Background Tasks (Log them as queued)
            yield json.dumps({"type": "log", "content": "Queueing background memory storage..."}) + "\n"
            
            # We need to trigger these after the response. 
            # In StreamingResponse, background tasks are passed to the response object.
            # We already added them to `background_tasks` object passed in.
            # However, we need to ensure they run. 
            # We can add them to the background_tasks dependency and FastAPI handles it after the stream closes.
            
            # Save assistant message
            background_tasks.add_task(crud.create_chat_message, db, current_user.id, "assistant", response_text)
            
            # Add to memory
            background_tasks.add_task(mem0_service.add_memory, f"User: {request.message}\nAssistant: {response_text}", str(current_user.id))
            
            yield json.dumps({"type": "log", "content": "All tasks queued. Done."}) + "\n"

        except Exception as e:
            logger.error(f"Error in chat stream: {e}")
            yield json.dumps({"type": "error", "content": str(e)}) + "\n"

    return StreamingResponse(event_generator(), media_type="application/x-ndjson", background=background_tasks)
