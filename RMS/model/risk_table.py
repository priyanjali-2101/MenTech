from sqlalchemy import Column, Integer, String, Text, DateTime ,ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.db import Base


class Risk(Base):
    __tablename__ = "risks"  # Database mein table ka naam

    id          = Column(Integer, primary_key=True, index=True)  
    title       = Column(String(200), nullable=False)            
    description = Column(Text, nullable=True)                    
    priority    = Column(String(50), default="Low")              
    status      = Column(String(50), default="Open")             
    category    = Column(String(100), nullable=True)             
    assigned_to = Column(String(100),ForeignKey("users.id"), nullable=True)             
    created_by  = Column(String(100), ForeignKey("users.id"),nullable=True)             
    due_date    = Column(String(50), nullable=True)              
    created_at  = Column(DateTime, default=func.now())           
    updated_at  = Column(DateTime, default=func.now(), onupdate=func.now())

    creator  = relationship("User", foreign_keys=[created_by], back_populates="risks_created")
    assignee = relationship("User", foreign_keys=[assigned_to], back_populates="risks_assigned")

    comments   = relationship("Comment", back_populates="risk")
    activities = relationship("Activity", back_populates="risk")