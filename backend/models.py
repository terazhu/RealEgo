from sqlalchemy import Column, Integer, String, Date, Text, DateTime
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True) # Foreign key logic managed manually or via relationship
    full_name = Column(String(100))
    birth_date = Column(Date)
    birth_place = Column(String(100))
    location = Column(String(100))
    family_info = Column(Text) # JSON or text description
    education_history = Column(Text)
    work_history = Column(Text)
    timeline_data = Column(Text) # JSON string storing the 9 categories
    history_limit = Column(Integer, default=100)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    role = Column(String(20)) # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
