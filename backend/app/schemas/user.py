from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: str

class User(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    user_id: int

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str
