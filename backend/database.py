from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Note: We might need to create the database first if it doesn't exist.
# For now, assuming the user 'tera' has permissions to create DB or it exists.
# I'll modify the URL to connect to 'mysql' db first to check/create if needed, 
# but for simplicity, let's assume 'realego' db is the target. 
# If connection fails, I'll add logic to create it.

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
