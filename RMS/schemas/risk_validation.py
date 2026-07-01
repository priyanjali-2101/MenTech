from pydantic import BaseModel
from typing import Optional


class RiskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "Low"        
    status: Optional[str] = "Open"         
    category: Optional[str] = None
    assigned_to: Optional[int] = None      
    due_date: Optional[str] = None
    mitigation: Optional[str] = None


class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[str] = None
    mitigation: Optional[str] = None


class RiskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    assigned_to: Optional[int] = None
    created_by: Optional[int] = None
    due_date: Optional[str] = None
    mitigation: Optional[str] = None

    class Config:
        from_attributes = True