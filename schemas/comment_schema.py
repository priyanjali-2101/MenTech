from pydantic import BaseModel
from typing import Optional


class CommentCreate(BaseModel):
    content: str
    risk_id: int


class CommentResponse(BaseModel):
    id: int
    content: str
    risk_id: int
    user_id: int

    class Config:
        from_attributes = True