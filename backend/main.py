from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base, SessionLocal
from routers import auth, users, chat, upload
import models
import crud, schemas
import os
import logging
import sys
import time
from sqlalchemy.orm import Session
import auth as auth_utils # Import auth module for password hashing

# Logging Configuration
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "server.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("RealEgo")

# Create DB tables
# In production, use Alembic. For now, auto-create.
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables checked/created.")
except Exception as e:
    logger.error(f"Error creating tables: {e}")

app = FastAPI(title="RealEgo Backend")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"Incoming connection from {client_host} - {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Completed {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
    return response

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
        logger.debug("Checking for default user 'tera'...")
        user = crud.get_user_by_username(db, "tera")
        if not user:
            logger.info("Creating default user 'tera'")
            user_in = schemas.UserCreate(username="tera", password="tera")
            try:
                crud.create_user(db, user_in)
                logger.info("Default user 'tera' created successfully.")
            except Exception as e:
                logger.error(f"Failed to create default user: {e}")
        else:
            logger.info("Default user 'tera' already exists. Resetting password to ensure validity.")
            try:
                hashed_password = auth_utils.get_password_hash("tera")
                user.hashed_password = hashed_password
                db.commit()
                logger.info("Password for 'tera' reset successfully.")
            except Exception as e:
                logger.error(f"Failed to reset password for 'tera': {e}")
    except Exception as e:
        logger.error(f"Error initializing user: {e}")
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    logger.info("Server is starting up...")
    
    # Run DB init logic manually here to ensure schemas are updated
    try:
        from init_db import init_db
        logger.info("Running DB initialization...")
        init_db()
    except Exception as e:
        logger.error(f"DB initialization failed: {e}")

    init_default_user()
    logger.info("Startup complete.")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server on port 8080...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
