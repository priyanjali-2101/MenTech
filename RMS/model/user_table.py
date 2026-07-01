from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False)  
    password   = Column(String(255), nullable=False)               
    role       = Column(String(50), default="Employee")            
    is_active  = Column(String(10), default="true")
    created_at = Column(DateTime, default=func.now())

    risks_created  = relationship("Risk", foreign_keys="Risk.created_by", back_populates="creator")
    risks_assigned = relationship("Risk", foreign_keys="Risk.assigned_to", back_populates="assignee")