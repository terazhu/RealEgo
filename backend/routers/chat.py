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
    
    # Save user message (Synchronous to ensure order and existence before reply)
    crud.create_chat_message(db, current_user.id, "user", request.message)

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
            
            # Use streaming chat
            completion = llm_service.chat(request.message, str(current_user.id), profile_dict, stream=True)
            
            yield json.dumps({"type": "log", "content": "LLM response stream started."}) + "\n"
            
            full_response = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    # Send partial chunk
                    yield json.dumps({"type": "response_chunk", "content": content}) + "\n"
            
            yield json.dumps({"type": "log", "content": "LLM response complete."}) + "\n"
            
            # 4. Background Tasks (Log them as queued)
            yield json.dumps({"type": "log", "content": "Queueing background memory storage..."}) + "\n"
            
            # Save assistant message
            background_tasks.add_task(crud.create_chat_message, db, current_user.id, "assistant", full_response)
            
            # Add to memory
            background_tasks.add_task(mem0_service.add_memory, f"User: {request.message}\nAssistant: {full_response}", str(current_user.id))
            
            yield json.dumps({"type": "log", "content": "All tasks queued. Done."}) + "\n"

        except Exception as e:
            logger.error(f"Error in chat stream: {e}")
            yield json.dumps({"type": "error", "content": str(e)}) + "\n"

    return StreamingResponse(
        event_generator(), 
        media_type="application/x-ndjson", 
        background=background_tasks,
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"}
    )
