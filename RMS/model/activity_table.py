from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base


class Activity(Base):
    __tablename__ = "activities"

    id          = Column(Integer, primary_key=True, index=True)
    action      = Column(String(255), nullable=False)   
    risk_id     = Column(Integer, ForeignKey("risks.id"), nullable=False)
    done_by     = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at  = Column(DateTime, default=func.now())

    # Relationships
    risk = relationship("Risk", back_populates="activities")
    user = relationship("User")