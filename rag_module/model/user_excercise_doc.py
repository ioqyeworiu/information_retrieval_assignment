from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from rag_module.util.database import Model
from datetime import datetime

class UserExerciseDoc(Model):
    __tablename__ = "user_exercise_docs"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    exercise_doc_id = Column(Integer, ForeignKey("exercise_docs.id"), primary_key=True)
    frequency = Column(Integer, nullable=True)
    last_practiced = Column(DateTime, nullable=True)
    last_viewed = Column(DateTime, nullable=True)
    ratings = Column(Integer, nullable=True)
    predicted_ratings = Column(Integer, nullable=True)

    created_at = Column(DateTime, nullable=True, default=datetime.now())
    updated_at = Column(DateTime, nullable=True, default=datetime.now(), onupdate=datetime.now())

    user = relationship("User", back_populates="user_exercise_docs")
    exercise_doc = relationship("ExerciseDoc", back_populates="user_exercise_docs")