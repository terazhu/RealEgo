from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base, SessionLocal
from routers import auth, users, chat, upload
import models
import crud, schemas
import os
from sqlalchemy.orm import Session

# Create DB tables
# In production, use Alembic. For now, auto-create.
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Error creating tables: {e}")

app = FastAPI(title="RealEgo Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for now, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(upload.router)

# Serve Frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/home.html")
async def read_home():
    return FileResponse(os.path.join(frontend_path, "home.html"))

# Initialize Default User
def init_default_user():
    db = SessionLocal()
    try:
        user = crud.get_user_by_username(db, "tera")
        if not user:
            print("Creating default user 'tera'")
            user_in = schemas.UserCreate(username="tera", password="tera")
            crud.create_user(db, user_in)
    except Exception as e:
        print(f"Error initializing user: {e}")
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    init_default_user()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
