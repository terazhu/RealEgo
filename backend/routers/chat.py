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

            # 2. Search Memory
            # Now explicitly showing the search step and waiting for it
            yield json.dumps({"type": "log", "content": "Searching relevant memories..."}) + "\n"
            memories = await mem0_service.search_memory(request.message, str(current_user.id))
            mem_count = len(memories) if memories else 0
            yield json.dumps({"type": "log", "content": f"Found {mem_count} relevant memories."}) + "\n"

            # 3. Call LLM
            yield json.dumps({"type": "log", "content": "Constructing prompt and waiting for LLM..."}) + "\n"
            
            # Use streaming chat (Async)
            completion = await llm_service.chat(request.message, str(current_user.id), profile_dict, stream=True)
            
            yield json.dumps({"type": "log", "content": "LLM response stream started."}) + "\n"
            
            full_response = ""
            first_chunk_received = False
            async for chunk in completion:
                # Force flush immediately at start of loop to ensure previous log is sent
                # Note: 'yield' in FastAPI streaming response usually pushes to network buffer.
                # If we want to ensure it goes out, we rely on the server/client not buffering.
                
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    
                    if not first_chunk_received:
                        first_chunk_received = True
                        yield json.dumps({"type": "log", "content": "First token received from LLM."}) + "\n"
                        # Force a small pause/yield to ensure the log packet is flushed separately
                        # This is a hack for some buffering proxies, but also helps browser UI render the log
                        # before the first text chunk if they arrive in same packet.
                        await asyncio.sleep(0.01) 

                    full_response += content
                    # Send partial chunk
                    yield json.dumps({"type": "response_chunk", "content": content}) + "\n"
            
            yield json.dumps({"type": "log", "content": "LLM response complete."}) + "\n"
            
            # 4. Background Tasks
            yield json.dumps({"type": "log", "content": "Queueing background memory storage..."}) + "\n"
            
            # Use asyncio.create_task for true non-blocking background work in async handler
            # FastAPI's background_tasks might run after the response closes, which is fine,
            # but here we want to log that we are done queueing.
            background_tasks.add_task(crud.create_chat_message, db, current_user.id, "assistant", full_response)
            
            # Add to memory (Async call in background task might need wrapper or sync method?)
            # BackgroundTasks runs in threadpool for sync, or event loop for async?
            # FastAPI BackgroundTasks supports async def.
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
