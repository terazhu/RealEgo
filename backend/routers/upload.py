from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import auth, models
from services.tos import tos_service

router = APIRouter(prefix="/upload", tags=["upload"])

@router.post("/")
async def upload_file(file: UploadFile = File(...), current_user: models.User = Depends(auth.get_current_user)):
    # Create a unique key
    import uuid
    file_ext = file.filename.split(".")[-1]
    object_key = f"user_{current_user.id}/{uuid.uuid4()}.{file_ext}"
    
    try:
        contents = await file.read()
        url = tos_service.upload_file(contents, object_key)
        return {"filename": file.filename, "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
