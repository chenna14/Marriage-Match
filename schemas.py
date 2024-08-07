from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import Column, Integer, String, ARRAY


class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: str
    city: str
    interests: str  # Properly annotate as List[str]

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    interests: Optional[str] = None  # Correctly annotate as Optional[List[str]]

class User(UserBase):
    id: int

    class Config:
        orm_mode = True
