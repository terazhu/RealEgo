from sqlalchemy import Column, Integer, String, Date, Text
from database import Base

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
