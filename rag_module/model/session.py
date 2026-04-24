from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from rag_module.util.database import Model

class Session(Model):
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, nullable=True, default=datetime.now())
    updated_at = Column(DateTime, nullable=True, default=datetime.now(), onupdate=datetime.now())

    user = relationship("User", back_populates="sessions")