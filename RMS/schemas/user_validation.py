from pydantic import BaseModel
from typing import Optional


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "Employee"


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: str

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    role: str