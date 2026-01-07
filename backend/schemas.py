from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    birth_place: Optional[str] = None
    location: Optional[str] = None
    family_info: Optional[str] = None
    education_history: Optional[str] = None
    work_history: Optional[str] = None

class ProfileUpdate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    user_id: int
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
