from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base


class Comment(Base):
    __tablename__ = "comments"

    id         = Column(Integer, primary_key=True, index=True)
    content    = Column(Text, nullable=False)
    risk_id    = Column(Integer, ForeignKey("risks.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    risk = relationship("Risk", back_populates="comments")
    user = relationship("User")