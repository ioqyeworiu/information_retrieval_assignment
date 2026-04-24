from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from rag_module.util.database import Model
from datetime import datetime

class ExerciseDoc(Model):
    __tablename__ = "exercise_docs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String, nullable=True)
    title = Column(String, nullable=True)
    muscles_used = Column(String, nullable=True)
    level = Column(String, nullable=True)
    instrument = Column(String, nullable=True)
    instruction = Column(String, nullable=True)
    image = Column(String, nullable=True)
    video = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=True, default=datetime.now())
    updated_at = Column(DateTime, nullable=True, default=datetime.now(), onupdate=datetime.now())

    user_exercise_docs = relationship("UserExerciseDoc", back_populates="exercise_doc")